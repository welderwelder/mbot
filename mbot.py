# coding: utf-8
import telegram, time, sys, os, re, platform
from telegram import ParseMode
from datetime import datetime, timedelta
import logging
import tokenbot                     # .gitignore !
import WazeRouteCalculator
import dfu                          # Data_File_Use: strings constants etc.
import pymongo

reload(sys)                         # after class-ing: err ascii decode heb str
sys.setdefaultencoding('UTF-8')     # still heb strings log lft->rgt reversed(?)

cnfg_file = "cnfg.txt"

# LOG:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)                       # up level setting for logger obj

formatter = logging.Formatter('%(asctime)s:%(name)s:   %(message)s')

file_handler = logging.FileHandler('mbot.log')      # .gitignore !
# file_handler.setLevel(logging.ERROR)              # if want to log error and above ==> .ERROR
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# DB:
pm_cli = pymongo.MongoClient(tokenbot.pm_cli_cre_con_inst_str)
pm_cli_db_mtftx = pm_cli.mtftx           # chk if "test"(db) exists, if not - would be created ~automatically~
msg_clct = pm_cli_db_mtftx.msg           # chk if "xxx"(collection) exists..            ~ ~ ~
crm_clct = pm_cli_db_mtftx.crm


#
#
# ___________________________________________________________________________
class Robot:
    def __init__(self, tokn):
        self.token = tokn
        self.bot = telegram.Bot(token=self.token)
        logger.info("bot init: " + str(self.bot))
        self.dyn_delay = 0.9

    # def get_bot(self):
    #     return self.bot

    #
    def get_lst_msg_bot(self):
        self.skippy = True
        try:
            # self.lst_msg = self.bot.get_updates()[-1].message     # take whole buffer(srvr_max=100) and take last.
            self.lst_msg = self.bot.get_updates(-1)[0].message      # 'forgets' all but last!
            self.lst_msg_id = self.lst_msg.message_id
            self.skippy = False
            self.dyn_delay = 0.9
        except telegram.error.TimedOut:
            print dfu.str_time_out.format(datetime.now())
            self.dyn_delay = 5
        except IndexError:
            print dfu.str_idx_err.format(datetime.now())
            self.dyn_delay = 10
        except Exception as e:
            logger.info(e)

    #
    def snd_msg(self, cht_id_to, msg_txt_new):
        try:
            self.bot.send_message(chat_id=cht_id_to, text=msg_txt_new,
                                  parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.info(e)

    #
    def get_f_lst_id(self):
        try:                                    # if os.path.exists(cnfg_file):
            f = open(cnfg_file, "r")
            self.f_rd_ln = f.readline()
            logger.info("get_f_lst_id: " + str(self.f_rd_ln))
            f.close()
        except Exception as e:
            logger.exception(e)

        return self.f_rd_ln

    #
    def upd_f_lst_id(self):
        try:
            f = open(cnfg_file, "r+")           # r+ The stream is positioned at the beginning of file  # f.seek(0)
            f.write(str(self.lst_msg_id) + "\n")
            logger.info("upd_f_lst_id: " + str(self.lst_msg))
            f.close()
        except Exception as e:
            logger.exception(e)
            sys.exit()                          # stop run - erroneous upd but level='info'


#
#
#
#
# _________________________________________________________________________________________________________________
class Msg:
    def __init__(self):
        self.from_adrs = tokenbot.from_address_dflt
        self.to_adrs = tokenbot.to_address_dflt

        self.cre_msg_txt_new = '`Default message`'

        # daily functionality:
        self.daily_dd_done = '00'                     # for daily_route() use
        self.dt_tm_now_prv = datetime.now()           # first time set:  ~~prevoius `now`~~
        self.daily_rt_tm = 0.0
        self.daily_rt_tm_prv = 0.0

    #
    def init_xtnd(self, i_analyze_msg):
        self.anlz_msg_cht_id = i_analyze_msg.chat_id
        self.anlz_msg_from_name = i_analyze_msg.chat['first_name']
        self.anlz_msg_last_name = i_analyze_msg.chat['last_name']
        self.anlz_msg_id = i_analyze_msg.message_id
        self.anlz_msg_txt = i_analyze_msg.text
        self.anlz_msg_ts = i_analyze_msg.date
        self.anlz_msg_rt_tm_optml_gnrtd = 0
        self.sw_fst_tm_crm_ins = False
        self.sw_upd_crm = False

        self.msg_data_2db = {'usr_id':     self.anlz_msg_cht_id,
                             # 'from_name': self.anlz_msg_from_name,
                             # 'last_name': self.anlz_msg_last_name,
                             'msg_id':     self.anlz_msg_id,
                             'txt':        self.anlz_msg_txt,
                             'ts':         self.anlz_msg_ts,
                             'i_o':        'i',
                             'mch':        platform.node()
                             }

        self.crm_data_2db = {'usr_id':     self.anlz_msg_cht_id,
                             'first_name': self.anlz_msg_from_name,
                             'last_name':  self.anlz_msg_last_name,
                             'home_adr':   tokenbot.from_address_dflt,
                             'work_adr':   tokenbot.to_address_dflt,
                             'ts':         datetime.now(),
                             'mch':        platform.node(),
                             'ver':        0
                             }

        try:
            msg_clct.insert(self.msg_data_2db)
        except Exception as e:
            logger.info(e)


    #
    def calc_route(self, i_from_adrs, i_to_adrs):
        o_cre_txt_msg = ' '
        rt_tm_optml = 0      # set val for case of abend while eeroneous input:"bashkilon"~~
        try:
            route = WazeRouteCalculator.WazeRouteCalculator(i_from_adrs,
                                                            i_to_adrs,
                                                            'IL'    # region
                                                            )
            rt_tm_optml, rt_dist_optml = route.calc_route_info()      # tuple
            all_rts_d = route.calc_all_routes_info()      # dict
            # print sorted(all_rts_d.values(),all_rts_d.keys()) ????????????????????????????????
            rt_lns_all = ''
            for ky, vl in all_rts_d.items():              # print ky, ':', vl
                rt_hb_str = ky
                rt_line = ''
                for chr in rt_hb_str:                     # fix readability of heb route string rcvd from wz server
                    if chr == u'\xd7':                              # evry heb char rcvd from wz starts: xd7
                        pass                                        # ==> chg by 2nd byte. replace func cannot chg 2bytes(?)
                    elif chr in dfu.dict_heb_chr_u8_ucode.keys():   # u'\x93':
                        rt_line += dfu.dict_heb_chr_u8_ucode[chr]     # u'\u05D3'
                    # elif chr.isdigit():
                        # rt_ln += u'\u05D9' + chr + u'\u05D9'      # attempt to fix directions of hebstr with numbrs
                    else:
                        rt_line += chr                    # rt_ln = rt_ln[::-1] # reverse string - print=rvrsd, send=ok

                vl_div, vl_mod = divmod(vl[0], 60)        # type(vl) = `tuple`
                if vl_div == 0:
                    rt_line_cur = "\n({:.0f}min,{:.0f}km){}".format(vl_mod, vl[1], rt_line)
                else:
                    rt_line_cur = "\n({:.0f}h{:.0f}min,{:.0f}km){}".format(vl_div,vl_mod, vl[1], rt_line)

                if int(vl[0]) == int(rt_tm_optml) and int(vl[1]) == int(rt_dist_optml):     # bold-up shortest route
                    rt_line_cur = dfu.b_s + rt_line_cur + dfu.b_e + u' \u2b05'              # <-- = arrow left

                rt_lns_all += rt_line_cur

            o_cre_txt_msg = \
                dfu.str_full_tm_dist.format(platform.node()[0],
                                            i_from_adrs,
                                            i_to_adrs            # rt_tm_optml, rt_dist_optml - omit only optml route line
                                            )
            o_cre_txt_msg += rt_lns_all
            logger.info(o_cre_txt_msg)
        except WazeRouteCalculator.WRCError as err:
            logger.info(err)
        except Exception as e:              # other cases, ex:erroneous input sent ==> abend
            logger.info(e)
            o_cre_txt_msg = '(' + platform.node()[0] + ') Error CALC route - check Source/Dest !!'

        return o_cre_txt_msg, rt_tm_optml


    #
    def get_prsn_dtl(self):
        # prs_dct_lst = filter(lambda person: person['Id'] == self.anlz_msg_cht_id, tokenbot.p_dtl_dicts_lst)
        try:
            self.per_dct_gdb_u = crm_clct.find_one({'usr_id': self.anlz_msg_cht_id, 'ver': 0}, {'_id':0})
                                                                                            # projection~filter-out
                                                                     #.limit(1)  #lmt instd: find_one - performance
            if self.per_dct_gdb_u == None:
                crm_clct.insert(self.crm_data_2db)
                self.sw_fst_tm_crm_ins = True
            else:
                self.from_adrs = self.per_dct_gdb_u['work_adr']
                self.to_adrs = self.per_dct_gdb_u['home_adr']
                self.anlz_msg_from_name = self.per_dct_gdb_u['first_name']
        except Exception as e:
            logger.info(e)

        # prs_get_dct = next((prsn for prsn in tokenbot.p_dtl_dicts_lst if prsn['Id'] == self.anlz_msg_cht_id), None)
        # if prs_get_dct:
        #     self.from_adrs = prs_get_dct["Work"]
        #     self.to_adrs = prs_get_dct["Home"]


    #
    def analyze_in_msg(self):
        if type(self.anlz_msg_txt).__name__ != 'unicode':       # in case of NON-text input: imoji/pic
            self.anlz_msg_txt = 'Override - input not text!'

        self.get_prsn_dtl()

        self.cre_msg_txt_new = dfu.str_greeting.format(self.anlz_msg_from_name,
                                                       platform.node(),
                                                       self.anlz_msg_txt
                                                       )
        if self.sw_fst_tm_crm_ins:
          self.cre_msg_txt_new += '.\n\nYou were added to the SYSTEM.'

        # "home"/"work"
        if self.anlz_msg_txt.lower() in (dfu.lst_str_hom_cmd + dfu.lst_str_wrk_cmd):
            if self.anlz_msg_txt.lower() in dfu.lst_str_wrk_cmd:
                self.from_adrs, self.to_adrs = self.to_adrs, self.from_adrs     # S W A P !!!
            self.cre_msg_txt_new, self.anlz_msg_rt_tm_optml_gnrtd\
                = self.calc_route(self.from_adrs, self.to_adrs)                 #[0]
        #              ##########
        # "HELP"
        elif self.anlz_msg_txt.lower() in dfu.lst_str_hlp_cmd:                  # case-insensitive
            self.cre_msg_txt_new = dfu.str_out_cmnds
        #
        #
        # "NAME="
        elif (any(ele in self.anlz_msg_txt.lower() for ele in dfu.lst_str_upd_nam_cmd) and
              not(self.sw_fst_tm_crm_ins)):
            self.crm_data_2db['first_name'] = self.anlz_msg_txt.split("=")[1]
            self.per_dct_gdb_u['first_name'] = self.anlz_msg_txt.split("=")[1]
            self.sw_upd_crm = True
        # "HOME="
        elif (any(ele in self.anlz_msg_txt.lower() for ele in dfu.lst_str_upd_hom_cmd) and
            not (self.sw_fst_tm_crm_ins)):
            self.crm_data_2db['home_adr'] = self.anlz_msg_txt.split("=")[1]
            self.per_dct_gdb_u['home_adr'] = self.anlz_msg_txt.split("=")[1]
            self.sw_upd_crm = True
        # "WORK="
        elif (any(ele in self.anlz_msg_txt.lower() for ele in dfu.lst_str_upd_wrk_cmd) and
            not (self.sw_fst_tm_crm_ins)):
            self.crm_data_2db['work_adr'] = self.anlz_msg_txt.split("=")[1]
            self.per_dct_gdb_u['work_adr'] = self.anlz_msg_txt.split("=")[1]
            self.sw_upd_crm = True
        else:
            pass

        if self.sw_upd_crm:
            try:
                # per_dct_gdb_u = crm_clct.find_one({'usr_id': self.anlz_msg_cht_id, 'ver': 0}, {'_id': 0})
                print self.per_dct_gdb_u
                crm_clct.update({'usr_id': self.anlz_msg_cht_id, 'ver': 0}, {'$set': {'ver': 1}})
                self.crm_data_2db['ver'] = 0
                crm_clct.insert(self.per_dct_gdb_u)
                self.cre_msg_txt_new = 'Updated Successfully :)'
            except Exception as e:
                logger.info(e)

        # SAVE MESSAGE --> DB:
        # DEFAULT=work-2-home (or  s w a p):
        # "/HOME","/WORK"
        # self.msg_data_2db.update({ --- causes duplicate key ~~ _id added automatically?~
        self.msg_data_2db = {'usr_id':  self.anlz_msg_cht_id,
                             'msg_id':  self.anlz_msg_id,
                             'txt':     self.cre_msg_txt_new,   # new generated text of message!
                             'ts':      datetime.now(),
                             'i_o':     'o',
                             'mch':     platform.node()
                             } #)
        if self.anlz_msg_rt_tm_optml_gnrtd != 0:
            self.msg_data_2db['rt_tm'] = int(self.anlz_msg_rt_tm_optml_gnrtd)
        try:
            msg_clct.insert(self.msg_data_2db)
        except Exception as e:
            logger.info(e)

        # return self.cre_msg_txt_new, self.rt_tm_optml_gnrtd


    #
    def daily_route(self):
        self.dt_tm_now = datetime.now()
        self.dt_tm_now_dd = self.dt_tm_now.strftime('%d')

        # TODO: init dt_tm_now_prv when date changes!!!
        # 'daily' TIMING is on:
        if ( self.dt_tm_now.strftime('%H') == dfu.daily_rt_scdl_hh_str and      # 15:mm
             self.dt_tm_now.strftime('%M') < dfu.daily_rt_scdl_mm_max_str ):    # HH:45
            # 'daily' NOT treated yet(by DD of cur date):
            if self.daily_dd_done != self.dt_tm_now_dd:
                # time interval reached:
                if self.dt_tm_now_prv < self.dt_tm_now - timedelta(hours=dfu.tm_sample_delta_hh,
                                                             minutes=dfu.tm_sample_delta_mm,
                                                             seconds=dfu.tm_sample_delta_ss):
                    self.daily_rt_tm = self.calc_route(self.from_adrs, self.to_adrs)[1]
                    # print daily_rt_tm

                    # TODO:
                    # if (first time for cur day and
                    #     self.daily_rt_tm > self.dfu.rt_tm_long ):
                    #     warning!
                    #
                    # self.daily_dd___ = self.dt_tm_now_dd    # 're-updated' but only when daily 'occurs'

                        # TODO: init daily_rt_tm_prv when date changes!!!
                        # DELTA check ?????:

                        # if self.daily_rt_tm > self.daily_rt_tm_prv + 1.1:
                        # print 'cur=', self.daily_rt_tm, '   prv=', self.daily_rt_tm_prv
                        # self.daily_rt_tm_prv = self.daily_rt_tm

                        # self.dt_tm_now_prv = self.dt_tm_now

                        #             # self.snd_msg(tokenbot.hi_auth_id_lst[0], Msg?.cre_msg_txt_new)
                        #             self.daily_dd_done = datetime.now().strftime('%d')
                        # if route_calc_warning_y
                        #     r.snd_msg


#
# ___________________________________________________________________________
# ___________________________________________________________________________
def main():
    running = True

    logger.info(dfu.str_start)                  # reference for RESTARTING..

    r = Robot(tokenbot.token_bot)

    m_flow = Msg()
    # m_daily = Msg()

    lst_id = r.get_f_lst_id()

    while running:
        time.sleep(r.dyn_delay)                 # (0.9)

        r.get_lst_msg_bot()
        if (not r.skippy):
            if r.lst_msg_id > int(lst_id):
                m_flow.init_xtnd(r.lst_msg)

                m_flow.analyze_in_msg()
                r.snd_msg(m_flow.anlz_msg_cht_id, m_flow.cre_msg_txt_new)

                r.upd_f_lst_id()
                lst_id = str(r.lst_msg_id)

        # m_daily.daily_route()
        # if msg not empty
        #     r.snd


#
# ___________________________________________________________________________
# ___________________________________________________________________________
if __name__ == "__main__":
        main()
# ___________________________________________________________________________
# ___________________________________________________________________________



