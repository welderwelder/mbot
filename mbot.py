import telegram, time, sys, os, re, platform
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
from_address = tokenbot.from_address_main
# to_address = tokenbot.to_address_main
region = 'IL'


#
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
            self.cht_id = self.lst_msg.chat_id
            self.from_name = self.lst_msg.chat["first_name"]
            self.msg_id = self.lst_msg.message_id
            self.msg_txt = self.lst_msg.text
            self.skippy = False
        except telegram.error.TimedOut:
            print dfu.str_time_out.format(datetime.now())
        except IndexError:
            print dfu.str_idx_err.format(datetime.now())
        except Exception as e:
            logger.info(e)

        return self.lst_msg

    def snd_msg(self, cht_id_to, msg_txt):
        try:
            self.bot.send_message(chat_id=cht_id_to, text=msg_txt)
        except Exception as e:
            logger.info(e)


#
#
#
#
# ___________________________________________________________________________
def get_f_lst_id():

    try:                                    # if os.path.exists(cnfg_file):
        f = open(cnfg_file, "r")
        f_rd_ln = f.readline()
        logger.info("get_f_lst_id: " +str(f_rd_ln))
        f.close()
    except Exception as e:
        logger.exception(e)

    return f_rd_ln


# ___________________________________________________________________________
def upd_f_lst_id(msg_id_last, msg_msg):

    try:
        f = open(cnfg_file, "r+")           # r+ The stream is positioned at the beginning of file  # f.seek(0)
        f.write(str(msg_id_last) + "\n")
        logger.info("upd_f_lst_id: " + str(msg_msg))
        f.close()
    except Exception as e:
        logger.exception(e)
        sys.exit()                   # stop run - erroneous upd but level='info'


#
#
#
#
# ___________________________________________________________________________
def cre_msg(cre_from_name, cre_msg_txt, cre_chat_id):
    sw_info = False
    if cre_chat_id == tokenbot.boss_id:     # boss_id~=123456789
        logger.info("Boss is here!")

    # if cre_chat_id in [tokenbot.boss_id, tokenbot.test_id]:
    sw_wz = False
    if re.compile('|'.join(dfu.str_wz_srch_lst), re.IGNORECASE).search(cre_msg_txt):
        sw_wz = True
        if cre_chat_id == tokenbot.boss_id:
            to_address = tokenbot.to_address_main
        elif cre_chat_id == tokenbot.test_id:
            to_address = tokenbot.to_address_test

        route = WazeRouteCalculator.WazeRouteCalculator(from_address,
                                                        to_address,
                                                        region
                                                        )
        try:
            rt_tm, rt_dist = route.calc_route_info()    # tuple
        except WazeRouteCalculator.WRCError as err:
            logger.info(err)

    rules_heb_qstn_str = [  # example of using rules/any/all:
                            u"\u05d0\u05d9\u05da"   in cre_msg_txt,  # eyh     unicode
                            u"\u05DE\u05D4"         in cre_msg_txt,  # ma
                            u"\u05DC\u05D0\u05DF"   in cre_msg_txt,  # lean
                            u"\u05DC\u05DE\u05D4"   in cre_msg_txt   # lama
                            ]

    # if cre_msg_txt == 'info' or cre_msg_txt == 'INFO' or cre_msg_txt == 'Info':
    if re.match("info", cre_msg_txt, flags=re.I):
        sw_info = True
    elif (   # search list of values in a `big` string
          (re.compile('|'.join(dfu.str_qstn_srch_lst), re.IGNORECASE).search(cre_msg_txt))
            or
           any(rules_heb_qstn_str)
          ):
        logger.info("rule!")
        cre_msg_txt_rule = dfu.str_qstn_rule_y
    else:
        cre_msg_txt_rule = dfu.str_qstn_rule_gen

    if sw_info:
        cre_msg_txt_new = dfu.str_rsrv_struct      # reservation structure description
    else:
        cre_msg_txt_new = dfu.str_greeting.format(cre_from_name,
                                                  platform.node(),
                                                  cre_msg_txt_rule,
                                                  cre_msg_txt
                                                  )
    if sw_wz:
        cre_msg_txt_new = dfu.str_full_tm_dist.format(from_address,
                                                      to_address,
                                                      rt_tm,
                                                      rt_dist
                                                      )
        logger.info("cre_msg_txt_new: " + str(cre_msg_txt_new))

    return cre_msg_txt_new


#
#
# ___________________________________________________________________________
# ___________________________________________________________________________
def main():
    running = True

    logger.info(dfu.str_start)                  # reference for RESTARTING..

    r = Robot(tokenbot.token_bot)

    lst_id = get_f_lst_id()

    while running:
        time.sleep(0.9)

        msg = r.get_lst_msg_bot()

        if (not r.skippy) and (r.msg_id > int(lst_id)):
            logger.info(dfu.str_is_cur_msg.format(str(r.msg_id),
                                                  str(r.cht_id),
                                                  r.msg_txt,
                                                  r.from_name
                                                  )
                        )

            msg_txt_new = cre_msg(r.from_name, r.msg_txt, r.cht_id)
            r.snd_msg(r.cht_id, msg_txt_new)
            upd_f_lst_id(r.msg_id, msg)
            lst_id = str(r.msg_id)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
        main()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



