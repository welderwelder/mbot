# coding: utf-8
import telegram, time, sys, os, re, platform
from telegram import ParseMode
from datetime import datetime, timedelta
import logging
import tokenbot                     # .gitignore !
import WazeRouteCalculator
import dfu                          # Data_File_Use: strings constants etc.
import pymongo
import urllib
import speech_recognition as sr     # pip install SpeechRecognition
import subprocess                   # to run ffmpeg install ffmpeg ? via website+build! + apt

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
vcb_clct = pm_cli_db_mtftx.vcb

# SR:
rcgzr = sr.Recognizer()


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
        # try:
        #     data = urllib.urlopen("https://www.google.com")
        # except e:
        #     logger.info('get_lst_msg_bot: NO NETWORK')
        #     logger.info(e)

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
            logger.info('get_lst_msg_bot:')
            logger.info(e)


    #
    def snd_msg(self, cht_id_to, msg_txt_new):
        try:
            self.bot.send_message(chat_id=cht_id_to, text=msg_txt_new,
                                  parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.info('snd_msg:')
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
class Msg():
    def __init__(self, inst_name):
        self.inst_name = inst_name
        self.from_adrs = self.src = tokenbot.from_address_dflt
        self.to_adrs = self.dest = tokenbot.to_address_dflt

        self.cre_msg_txt_new = '`Default message`'

        # daily functionality:
        # self.daily_dd_done = '00'                     # for daily_route() use
        self.dr_sw_warn = False
        self.dr_now_prv = datetime.now() - timedelta(days=1)
        self.dr_rt_tm = 0.0
        self.dr_rt_tm_prv = 0.0
        self.dr_l_tms = [0, 0, 0]

    #
    def init_xtnd(self, i_analyze_msg_r):
        self.anlz_msg_cht_id = i_analyze_msg_r.chat_id
        self.anlz_msg_from_name = i_analyze_msg_r.chat['first_name']
        self.anlz_msg_last_name = i_analyze_msg_r.chat['last_name']
        self.anlz_msg_id = i_analyze_msg_r.message_id
        self.anlz_msg_txt = i_analyze_msg_r.text
        self.anlz_msg_ts = i_analyze_msg_r.date
        self.anlz_msg_rt_tm_optml_gnrtd = 0
        self.sw_fst_tm_crm_ins = False
        self.sw_upd_crm = False
        self.anlz_msg_r_obj = i_analyze_msg_r
        self.v_msg_fid = None
        self.p_msg_fid = None
        self.f_nam_wav = None

        # if self.anlz_msg_txt == None:
        #     self.anlz_msg_txt = 'NOT text'
        self.msg_data_2db = {'usr_id':     self.anlz_msg_cht_id,
                             # 'from_name': self.anlz_msg_from_name,
                             # 'last_name': self.anlz_msg_last_name,
                             'msg_id':     self.anlz_msg_id,
                             'txt':        self.anlz_msg_txt,
                             'ts':         self.anlz_msg_ts,
                             'i_o':        'i',
                             'mch':        platform.node()
                             }
        try:
            msg_clct.insert(self.msg_data_2db)
        except Exception as e:
            logger.info('init_xtnd:')
            logger.info(e)

        self.crm_data_2db = {'usr_id':     self.anlz_msg_cht_id,
                             'first_name': self.anlz_msg_from_name,
                             'last_name':  self.anlz_msg_last_name,
                             'home_adr':   tokenbot.from_address_dflt,
                             'work_adr':   tokenbot.to_address_dflt,
                             'ts':         datetime.now(),
                             'mch':        platform.node(),
                             'ver':        0
                             }


    #
    def calc_route(self, i_from_adrs, i_to_adrs):
        # o_cre_txt_msg = ' '
        o_cre_txt_msg = \
            dfu.str_full_tm_dist.format(platform.node()[0],
                                        i_from_adrs,
                                        i_to_adrs  # rt_tm_optml, rt_dist_optml - omit only optml route line
                                        )
        rt_tm_optml = 0      # set val for case of abend while eeroneous input:"bashkilon"~~
        try:
            route = WazeRouteCalculator.WazeRouteCalculator(i_from_adrs
                                                            , i_to_adrs
                                                            , 'IL'       # region
                                                            , log_lvl=None
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

            o_cre_txt_msg += rt_lns_all
            if self.inst_name != 'dr':
                logger.info(o_cre_txt_msg)
        # except WazeRouteCalculator.WRCError as err:
        #     logger.info(err)
        except Exception as e:              # other cases, ex:erroneous input sent ==> abend
            logger.info('calc_route:')
            logger.info(e)
            o_cre_txt_msg += '\n Error CALC route - check Source/Dest !!'

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
                self.per_dct_gdb_u = self.crm_data_2db  # init for case of first timer
            else:
                self.from_adrs = self.per_dct_gdb_u['work_adr']
                self.to_adrs = self.per_dct_gdb_u['home_adr']
                self.anlz_msg_from_name = self.per_dct_gdb_u['first_name']
        except Exception as e:
            logger.info('get_prsn_dtl:')
            logger.info(e)

            # prs_get_dct = next((prsn for prsn in tokenbot.p_dtl_dicts_lst if prsn['Id'] == self.anlz_msg_cht_id), None)
            # if prs_get_dct:
            #     self.from_adrs = prs_get_dct["Work"]
            #     self.to_adrs = prs_get_dct["Home"]


    #
    def v_msg_rcgz(self):
        try:
            f_nam = "voc/msg-" + platform.node()[0] + '-' + self.v_msg_fid + '-' \
                    + str(self.anlz_msg_cht_id) + '-' + str(datetime.now()) + ".oga"
            urllib.urlretrieve(self.v_msg_f_pth, f_nam)
            self.f_nam_wav = f_nam.replace(".oga",".wav")

            nl = open(os.devnull, 'wb')
            process = subprocess.call(['ffmpeg', '-i', f_nam, self.f_nam_wav], stdout=nl, stderr=nl)

            os.remove(f_nam)

            v_msg_wav_af = sr.AudioFile(self.f_nam_wav)

            with v_msg_wav_af as source:
                audio = rcgzr.record(source)   # print type(audio)

            self.anlz_rcgz_lst = rcgzr.recognize_google(audio, show_all=True)
            print self.anlz_rcgz_lst
            if len(self.anlz_rcgz_lst) > 0:
                lst_rcgz = [dict['transcript'] for dict in self.anlz_rcgz_lst["alternative"]]
                print lst_rcgz
                vcb_fnd = lst_rcgz[0]
                for mmbr in lst_rcgz:       # [u'a lot', : u'eilat']
                    vcb_chk = vcb_clct.find_one({'vcb_val': mmbr.lower()}) #---> ramat gan - 2 words ??????
                    if vcb_chk:
                        vcb_fnd = mmbr
                        print 'Found match!'   # -------------> need to look for LONGEST match !!!!!!
                        print mmbr
                        # [u'rehovot to Ramat Gan', u'rehovot to Ramat gun', u'to Ramat Gan']
                        # TODO:
                        # else:
                        #     fine tuning:  mmbr.split + chk num of db fits
                self.anlz_msg_txt = vcb_fnd
        except Exception as e:
            logger.info('v_msg_rcgz:')
            logger.info(e)


    #
    def chk_msg_type(self):
        if type(self.anlz_msg_txt).__name__ != 'unicode':        # in case of NON-text input: imoji/pic/voice
            self.anlz_msg_txt = 'Override - input NOT valid!'

            if self.anlz_msg_r_obj.voice != None:                # print r.lst_msg.photo[0]['file_id']
                self.v_msg_fid = self.anlz_msg_r_obj.voice['file_id']  # exmpl: .voice gets "None" if pic send !
                self.anlz_msg_txt = 'voice msg: ' + self.v_msg_fid
            elif len(self.anlz_msg_r_obj.photo) > 0:                # photo list always returned
                self.p_msg_fid = self.anlz_msg_r_obj.photo[0]['file_id']
                self.anlz_msg_txt = 'picture: ' + self.p_msg_fid

    #
    def analyze_txt_in_msg(self):
        self.get_prsn_dtl()

        self.cre_msg_txt_new = dfu.str_greeting.format(self.anlz_msg_from_name,
                                                       platform.node(),
                                                       self.anlz_msg_txt
                                                       )
        if self.sw_fst_tm_crm_ins:
            self.cre_msg_txt_new += '.\n\nYou were added to the SYSTEM.'

        #
        # "home" <---> "work"     DEFAULT=work-2-home (or  s w a p)...
        if self.anlz_msg_txt.lower() in (dfu.lst_str_hom_cmd + dfu.lst_str_wrk_cmd):
            if self.anlz_msg_txt.lower() in dfu.lst_str_wrk_cmd:
                self.from_adrs, self.to_adrs = self.to_adrs, self.from_adrs     # S W A P !!!
            self.src, self.dest = self.from_adrs, self.to_adrs
            self.cre_msg_txt_new, self.anlz_msg_rt_tm_optml_gnrtd= self.calc_route(self.src, self.dest)
        #                                                               ^^^^^^^^^^
        # "src to dest" ------->
        elif dfu.str_to_opr in self.anlz_msg_txt.lower():
            l_msg_txt_splt = self.anlz_msg_txt.split()
            print l_msg_txt_splt
            i = 0
            for w in l_msg_txt_splt:
                if w.lower() in dfu.d_abbrv:
                    l_msg_txt_splt[i] = dfu.d_abbrv[w.lower()]
                i += 1
            str_msg_txt_chkd = ' '.join(l_msg_txt_splt)

            self.src = str_msg_txt_chkd.split(dfu.str_to_opr)[0]
            self.dest = str_msg_txt_chkd.split(dfu.str_to_opr)[1]
            # if any(ele in src.lower() for ele in dfu.lst_wrk_spc_str):
            if self.src.lower() in dfu.lst_str_wrk_cmd:
                self.src = self.from_adrs    #from work
            if self.src.lower() in dfu.lst_str_hom_cmd:
                self.src = self.to_adrs      #from home

            if self.dest.lower() in dfu.lst_str_wrk_cmd:
                self.dest = self.from_adrs    #to work
            if self.dest.lower() in dfu.lst_str_hom_cmd:
                self.dest = self.to_adrs      #to home

            self.cre_msg_txt_new, self.anlz_msg_rt_tm_optml_gnrtd = self.calc_route(self.src, self.dest)
        #                                                                ^^^^^^^^^^
        #
        # "HELP"/"info"
        elif self.anlz_msg_txt.lower() in dfu.lst_str_hlp_cmd:  # case-insensitive
            r1, r2, r3, r4 = tokenbot.get_rndm().split('|')
            self.cre_msg_txt_new = dfu.str_out_cmnds.format(r1, r2, r3, r4) \
                                   + dfu.str_per_dtl.format(platform.node()[0],
                                                            self.per_dct_gdb_u['home_adr'],
                                                            self.per_dct_gdb_u['work_adr'])
        #
        # "NAME="
        elif (any(ele in self.anlz_msg_txt.lower() for ele in dfu.lst_str_upd_nam_cmd) and
                  not(self.sw_fst_tm_crm_ins)):
            self.crm_data_2db['first_name'] = self.anlz_msg_txt.split("=")[1]
            self.per_dct_gdb_u['first_name'] = self.anlz_msg_txt.split("=")[1]
            self.sw_upd_crm = True
        #
        # "HOME="
        elif (any(ele in self.anlz_msg_txt.lower() for ele in dfu.lst_str_upd_hom_cmd) and
                  not (self.sw_fst_tm_crm_ins)):
            self.crm_data_2db['home_adr'] = self.anlz_msg_txt.split("=")[1]
            self.per_dct_gdb_u['home_adr'] = self.anlz_msg_txt.split("=")[1]
            self.sw_upd_crm = True
        #
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
                crm_clct.update({'usr_id': self.anlz_msg_cht_id, 'ver': 0}, {'$set': {'ver': 1}})
                self.per_dct_gdb_u['ver'] = 0
                self.per_dct_gdb_u['mch'] = platform.node()
                self.per_dct_gdb_u['ts'] = datetime.now()
                crm_clct.insert(self.per_dct_gdb_u)
                self.cre_msg_txt_new = 'Updated Successfully :)'
            except Exception as e:
                logger.info('upd crm')
                logger.info(e)

        self.ins_msg_db()


    #
    def ins_msg_db(self):
        # SAVE MESSAGE --> DB:
        # self.msg_data_2db.update({ --- causes duplicate key ~~ _id added automatically?~
        self.msg_data_2db = {'usr_id': self.anlz_msg_cht_id,
                             'msg_id': self.anlz_msg_id,
                             'txt': self.cre_msg_txt_new,  # new generated text of message!
                             'ts': datetime.now(),
                             'i_o': 'o',
                             'mch': platform.node()
                             }
        if self.f_nam_wav != None:
            self.msg_data_2db['fnam'] = self.f_nam_wav

        if self.anlz_msg_rt_tm_optml_gnrtd != 0:
            self.msg_data_2db['rt_tm'] = int(self.anlz_msg_rt_tm_optml_gnrtd)

            try:  # save word of legit~reacheable address word by word + src + dst + src-to-dst
                expr = self.src + ' to ' + self.dest
                l_wrd_expr = expr.split()   # print 'src: ', src, ' dest: ', dest ' list of words: '
                for w in l_wrd_expr:
                    vcb_chk = vcb_clct.find_one({'vcb_val': w.lower()})
                    if not vcb_chk:  #
                        vcb_clct.insert({'vcb_val': w.lower()})

                vcb_chk = vcb_clct.find_one({'vcb_val': self.src.lower()})
                if not vcb_chk:  # ```
                    vcb_clct.insert({'vcb_val': self.src.lower()})

                vcb_chk = vcb_clct.find_one({'vcb_val': self.dest.lower()})
                if not vcb_chk:  # ```
                    vcb_clct.insert({'vcb_val': self.dest.lower()})

                vcb_data_2db = {'vcb_val': expr.lower(),
                                'rt_tm': int(self.anlz_msg_rt_tm_optml_gnrtd),    # for statistical use!!
                                'ts': datetime.now(),
                                }
                vcb_clct.insert(vcb_data_2db)

            except Exception as e:
                logger.info('anlz_..insert vcb:')
                logger.info(e)

        try:
            msg_clct.insert(self.msg_data_2db)
        except Exception as e:
            logger.info('anlz_..insert msg')
            logger.info(e)


    #
    def daily_route(self):
        self.anlz_msg_cht_id = tokenbot.dr_usr_id
        self.get_prsn_dtl()
        self.dr_now = datetime.now()
        self.dr_start = self.dr_now.replace(hour=dfu.dr_scdl_tm_start[0], minute=dfu.dr_scdl_tm_start[1])
        self.dr_end = self.dr_now.replace(hour=dfu.dr_scdl_tm_end[0], minute=dfu.dr_scdl_tm_end[1])

        # 'daily' TIMING is on:
        if (self.dr_start < self.dr_now < self.dr_end and
                        0 < self.dr_now.weekday()+2 < 6):                   #starts from 0, 1st dow=monday
            # time interval reached?:
            if self.dr_now_prv < self.dr_now - timedelta(minutes=dfu.tm_delta_mm, seconds=dfu.tm_delta_ss):
                self.cre_msg_txt_new, self.dr_rt_tm = self.calc_route(self.from_adrs, self.to_adrs)

                # first time for cur day: prv(d)<>now(d) ==> first time only!
                if self.dr_now_prv.strftime('%D') != self.dr_now.strftime('%D'):
                    self.dr_l_tms = [0, 0, 0]
                    if self.dr_rt_tm > dfu.rt_tm_long:
                        self.dr_sw_warn = True
                        self.cre_msg_txt_new = 'FIRST WARNING!!! \n' + self.cre_msg_txt_new

                self.dr_l_tms.pop(0)                       # [1,2,3]-->[2,3]
                self.dr_l_tms.append(self.dr_rt_tm)        # a.append(1)    [2,3]-->[2,3,4]
                if self.dr_l_tms[0] != 0:
                    if self.dr_l_tms[0] * dfu.jmp_prc < self.dr_l_tms[2]:
                        self.dr_wrn_cnt += 1
                        self.dr_sw_warn = True
                        self.cre_msg_txt_new = 'WARNING!!!\n   WARNING!!!\n' + self.cre_msg_txt_new


            self.dr_now_prv = self.dr_now




                # self.daily_dd___ = self.dt_tm_now_dd    # 're-updated' but only when daily 'occurs'

                # if self.dr_rt_tm > self.dr_rt_tm_prv + 1.1:
                # print 'cur=', self.dr_rt_tm, '   prv=', self.dr_rt_tm_prv
                # self.dr_rt_tm_prv = self.dr_rt_tm

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

    m_flow = Msg('flw')
    m_dr = Msg('dr')    #daily route

    lst_id = r.get_f_lst_id()

    while running:
        time.sleep(r.dyn_delay)                 # (0.9)

        r.get_lst_msg_bot()
        if (not r.skippy):
            if r.lst_msg_id > int(lst_id):
                m_flow.init_xtnd(r.lst_msg)

                m_flow.chk_msg_type()
                if m_flow.v_msg_fid != None:
                    m_flow.v_msg_f_pth = r.bot.get_file(m_flow.v_msg_fid)['file_path']
                    m_flow.v_msg_rcgz()

                m_flow.analyze_txt_in_msg()

                r.snd_msg(m_flow.anlz_msg_cht_id, m_flow.cre_msg_txt_new)

                r.upd_f_lst_id()
                lst_id = str(r.lst_msg_id)

        m_dr.daily_route()
        if m_dr.dr_sw_warn:
            r.snd_msg(m_dr.anlz_msg_cht_id, m_dr.cre_msg_txt_new)
            m_dr.dr_sw_warn = False


#
# ___________________________________________________________________________
# ___________________________________________________________________________
if __name__ == "__main__":
        main()
# ___________________________________________________________________________
# ___________________________________________________________________________



