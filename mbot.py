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

    # def get_bot(self):
    #     return self.bot

    def get_lst_msg_bot(self):
        self.skippy = True
        try:
            self.lst_msg = self.bot.get_updates()[-1].message
            self.lst_msg_id = self.lst_msg.message_id
            self.skippy = False
        except telegram.error.TimedOut:
            print dfu.str_time_out.format(datetime.now())
        except IndexError:
            print dfu.str_idx_err.format(datetime.now())
        except Exception as e:
            logger.info(e)

        return self.lst_msg

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


#
# ___________________________________________________________________________
class Msg:
    def __init__(self, analyze_msg):
        # self.sw_msg_wz = False
        self.from_adrs = tokenbot.from_address_dflt
        self.to_adrs = tokenbot.to_address_dflt

        self.anlz_msg = analyze_msg

        # self.sw_lst_msg_hi_auth_id = False
        self.anlz_msg_cht_id = analyze_msg.chat_id
        if self.anlz_msg_cht_id in tokenbot.hi_auth_id_lst:
        #     self.sw_anlz_msg_hi_auth_id = True
            self.from_adrs = tokenbot.from_address_main
            self.to_adrs = tokenbot.to_address_main

        self.anlz_msg_from_name = analyze_msg.chat["first_name"]
        self.anlz_msg_id = analyze_msg.message_id
        self.anlz_msg_txt = analyze_msg.text
        self.cre_msg_txt_new = '`Default mesage`'

    def analyze_in_msg(self):
        if re.compile('|'.join(dfu.str_in_cmd_hom + dfu.str_in_cmd_wrk),
                      re.IGNORECASE).search(self.anlz_msg_txt):
            # self.sw_msg_wz = True
            # def cre_route(self):
            if self.anlz_msg_txt.lower() in dfu.str_in_cmd_wrk:        # swap
                self.from_adrs, self.to_adrs = self.to_adrs, self.from_adrs

            try:
                route = WazeRouteCalculator.WazeRouteCalculator(self.from_adrs,
                                                                self.to_adrs,
                                                                'IL'    # region
                                                                )
                rt_tm, rt_dist = route.calc_route_info()            # tuple
                self.cre_msg_txt_new = \
                    dfu.str_full_tm_dist.format(self.from_adrs,
                                                self.to_adrs,
                                                rt_tm,
                                                rt_dist
                                                )
            except WazeRouteCalculator.WRCError as err:
                logger.info(err)
        elif self.anlz_msg_txt.lower() in dfu.str_qstn_srch_lst:        # case-insensitive
            self.cre_msg_txt_new = dfu.str_out_cmnds
        else:
            self.cre_msg_txt_new = dfu.str_greeting.format(self.anlz_msg_from_name,
                                                           platform.node(),
                                                           self.anlz_msg_txt
                                                           )
        return self.cre_msg_txt_new


# ___________________________________________________________________________
# ___________________________________________________________________________
def main():
    running = True

    logger.info(dfu.str_start)                  # reference for RESTARTING..

    r = Robot(tokenbot.token_bot)

    lst_id = r.get_f_lst_id()

    while running:
        time.sleep(0.9)

        m = Msg(r.get_lst_msg_bot())

        if (not r.skippy) and (r.lst_msg_id > int(lst_id)):

            r.snd_msg(m.anlz_msg_cht_id, m.analyze_in_msg())

            r.upd_f_lst_id()
            lst_id = str(r.lst_msg_id)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
        main()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



