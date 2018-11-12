# coding: utf-8
import telegram, time, sys, os, re, platform
from telegram import ParseMode
from datetime import datetime
import logging
import tokenbot                     # .gitignore !
import WazeRouteCalculator
import dfu                          # Data_File_Use: strings constants etc.

reload(sys)                         # after class-ing: err ascii decode heb str
sys.setdefaultencoding('UTF-8')     # still heb strings log lft->rgt reversed(?)

cnfg_file = "cnfg.txt"


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


#
#
# ___________________________________________________________________________
class Robot:
    def __init__(self, tokn):
        self.token = tokn
        self.bot = telegram.Bot(token=self.token)
        logger.info("bot init: " + str(self.bot))
        self.dyn_delay = 0.9
        self.daily_dd = '00'

    # def get_bot(self):
    #     return self.bot

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

    def snd_msg(self, cht_id_to, msg_txt_new):
        try:
            self.bot.send_message(chat_id=cht_id_to, text=msg_txt_new,
                                  parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.info(e)

    def get_f_lst_id(self):
        try:                                    # if os.path.exists(cnfg_file):
            f = open(cnfg_file, "r")
            self.f_rd_ln = f.readline()
            logger.info("get_f_lst_id: " + str(self.f_rd_ln))
            f.close()
        except Exception as e:
            logger.exception(e)

        return self.f_rd_ln

    def upd_f_lst_id(self):
        try:
            f = open(cnfg_file, "r+")           # r+ The stream is positioned at the beginning of file  # f.seek(0)
            f.write(str(self.lst_msg_id) + "\n")
            logger.info("upd_f_lst_id: " + str(self.lst_msg))
            f.close()
        except Exception as e:
            logger.exception(e)
            sys.exit()                          # stop run - erroneous upd but level='info'

    def daily_route(self):
        if self.daily_dd != datetime.now().strftime('%d'):
           if datetime.now().strftime('%H') == '15':      # strftime('%H:%M') 2018-11-07 11:57:53.238483
                Msg.from_adrs = tokenbot.from_address_main
                Msg.to_adrs = tokenbot.to_address_main
                Msg.calc_route()    # ????????????????????????????????????????????????????????????????
                self.snd_msg(tokenbot.hi_auth_id_lst[0], cre_msg_txt_new)
                self.daily_dd = datetime.now().strftime('%d')


#
#
# ___________________________________________________________________________
class Msg:
    def __init__(self, analyze_msg):
        self.from_adrs = tokenbot.from_address_dflt
        self.to_adrs = tokenbot.to_address_dflt

        self.anlz_msg = analyze_msg

        # self.msg_prs_hi_auth_id = False
        self.anlz_msg_cht_id = analyze_msg.chat_id

        self.anlz_msg_from_name = analyze_msg.chat["first_name"]
        self.anlz_msg_id = analyze_msg.message_id
        self.anlz_msg_txt = analyze_msg.text
        self.cre_msg_txt_new = '`Default mesage`'

    def calc_route(self):
        try:
            route = WazeRouteCalculator.WazeRouteCalculator(self.from_adrs,
                                                            self.to_adrs,
                                                            'IL'    # region
                                                            )
            rt_tm, rt_dist = route.calc_route_info()    # tuple
            all_rts_d = route.calc_all_routes_info()    # dict
            print sorted(all_rts_d.values(),all_rts_d.keys())
            rt_lns_all = ''
            for ky, vl in all_rts_d.items():                        # print ky, ':', vl
                rt_hb_str = ky
                rt_ln = ''
                for chr in rt_hb_str:
                    if chr == u'\xd7':                              # evry heb char rcvd from wz starts: xd7
                        pass                                        # ==> chg by 2nd byte. replace func cannot chg 2bytes(?)
                    elif chr in dfu.dict_heb_chr_u8_ucode.keys():   # u'\x93':
                        rt_ln += dfu.dict_heb_chr_u8_ucode[chr]     # u'\u05D3'
                    # elif chr.isdigit():
                        # rt_ln += u'\u05D9' + chr + u'\u05D9'
                    else:
                        rt_ln += chr                      # rt_ln = rt_ln[::-1] # reverse string - print=rvrsd, send=ok
                vl_div, vl_mod = divmod(vl[0], 60)        # type(vl) = `tuple`
                if vl_div == 0:
                    rt_lns_all += "\n({:.0f}min,{:.0f}km){}".format(vl_mod, vl[1], rt_ln)
                else:
                    rt_lns_all += "\n({:.0f}h{:.0f}min,{:.0f}km){}".format(vl_div,vl_mod, vl[1], rt_ln)
            self.cre_msg_txt_new = \
                dfu.str_full_tm_dist.format(platform.node()[0],
                                            self.from_adrs,
                                            self.to_adrs,
                                            rt_tm,
                                            rt_dist
                                            )
            self.cre_msg_txt_new += rt_lns_all
            logger.info(self.cre_msg_txt_new)
        except WazeRouteCalculator.WRCError as err:
            logger.info(err)

    def get_prsn_dtl(self):
        # prs_dct_lst = filter(lambda person: person['Id'] == self.anlz_msg_cht_id, tokenbot.p_dtl_dicts_lst)
        prs_get_dct = next((prsn for prsn in tokenbot.p_dtl_dicts_lst if prsn['Id'] == self.anlz_msg_cht_id), None)
        if prs_get_dct:
            self.from_adrs = prs_get_dct["Work"]
            self.to_adrs = prs_get_dct["Home"]

    # def chk_auth(self):
    #     if self.anlz_msg_cht_id in tokenbot.hi_auth_id_lst:
    #             self.msg_prs_hi_auth_id = True

    def analyze_in_msg(self):
        if type(self.anlz_msg_txt).__name__ != 'unicode':       # in case of NON-text input: imoji/pic
            self.anlz_msg_txt = 'Override - input not text!'

        self.cre_msg_txt_new = dfu.str_greeting.format(self.anlz_msg_from_name,
                                                       platform.node(),
                                                       self.anlz_msg_txt
                                                       )
        self.get_prsn_dtl()

        # DEFAULT=work-2-home (or swap):
        # search "comands strings" in input message:
        # if re.compile('|'.join(dfu.lst_str_in_cmd_hom + dfu.lst_str_in_cmd_wrk),
        #               re.IGNORECASE).search(self.anlz_msg_txt):
        if self.anlz_msg_txt.lower() in (dfu.lst_str_in_cmd_hom + dfu.lst_str_in_cmd_wrk):
            if self.anlz_msg_txt.lower() in dfu.lst_str_in_cmd_wrk:     # swap
                self.from_adrs, self.to_adrs = self.to_adrs, self.from_adrs

            self.calc_route()
        # "pause comp_name":
        # elif (self.anlz_msg_txt.lower().startswith(dfu.str_in_cmd_pause) and
        #       len(self.anlz_msg_txt.lower().split(' ')) == 2):
        #     if self.anlz_msg_txt.lower().split(' ')[1] == platform.node():
        #         self.chk_auth()
        #         if self.msg_prs_hi_auth_id:
        #             self.cre_msg_txt_new += '\n* * * P A U S E * * *'
        # help/commands/info~:
        elif self.anlz_msg_txt.lower() in dfu.str_help_cmd_lst:        # case-insensitive
            self.cre_msg_txt_new = dfu.str_out_cmnds
        else:
            pass

        return self.cre_msg_txt_new


#
# ___________________________________________________________________________
# ___________________________________________________________________________
def main():
    running = True

    logger.info(dfu.str_start)                  # reference for RESTARTING..

    r = Robot(tokenbot.token_bot)

    lst_id = r.get_f_lst_id()

    while running:
        time.sleep(r.dyn_delay)                 # (0.9)

        r.get_lst_msg_bot()

        if (not r.skippy):
            if r.lst_msg_id > int(lst_id):
                m = Msg(r.lst_msg)
                r.snd_msg(m.anlz_msg_cht_id, m.analyze_in_msg())

                r.upd_f_lst_id()
                lst_id = str(r.lst_msg_id)


        r.daily_route()


#
# ___________________________________________________________________________
# ___________________________________________________________________________
if __name__ == "__main__":
        main()
# ___________________________________________________________________________
# ___________________________________________________________________________



