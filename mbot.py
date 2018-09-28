import telegram, time, sys, os, re, platform
from datetime import datetime
import logging
import tokenbot                                     # .gitignore !

bot = telegram.Bot(token=tokenbot.token_bot)        # .gitignore !

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


# ___________________________________________________________________________
def chk_f_sw_i_run():

    try:                                    # if os.path.exists(cnfg_file):
        f = open(cnfg_file, "r")
        f_rd_ln = f.readline()
        f.close()
    except Exception as e:
        logger.exception(e)
        sys.exit('ERROR:' + cnfg_file + "  ---> READ file does not existsss!!!!")

    return f_rd_ln


# ___________________________________________________________________________
def upd_f_sw_i_run(msg_id_last, msg_msg):

    try:                                    # if os.path.exists(cnfg_file):
        f = open(cnfg_file, "r+")           # r+ The stream is positioned at the beginning of file  # f.seek(0)
        f.write(str(msg_id_last) + "\n")
        logger.info(str(msg_msg))
        f.close()
    except Exception as e:
        logger.exception(e)
        sys.exit("ERROR:" + cnfg_file + "  --->    WRITE  file does not existsss!!!!")


# ___________________________________________________________________________
def cre_msg(cre_from_name, cre_msg_txt, cre_chat_id):
    sw_info = False
    if cre_chat_id == tokenbot.boss_id:     # boss_id~=123456789
        logger.info("Boss is here!")

    rules_heb_questn_str = [
                u"\u05d0\u05d9\u05da" in cre_msg_txt,      # eyh     unicode
                u"\u05DE\u05D4"       in cre_msg_txt,      # ma
                u"\u05DC\u05D0\u05DF" in cre_msg_txt,      # lean
                u"\u05DC\u05DE\u05D4" in cre_msg_txt       # lama
                # re.match("who", cre_msg_txt, flags=re.I),
             ]

    search_list = ['who', 'what', 'why', 'how', '.*\?', 'where']
    if cre_msg_txt == 'info'  or  cre_msg_txt == 'INFO'  or  cre_msg_txt == 'Info':
        sw_info = True
    elif (
          (re.compile('|'.join(search_list), re.IGNORECASE).search(cre_msg_txt)) or
           any(rules_heb_questn_str)           # if any(rules_heb_questn_str): #if all(rules_heb_questn_str):
          ):
        logger.info("rule!")
        cre_msg_txt_rule = "serving  MATAF TAXI reservations, type `info` for reservation instructions, "
    else:
        cre_msg_txt_rule = 'type `info` for reservation instructions,'

    if sw_info:
        cre_msg_txt_new = ("reservation structure:\n    Source \n      dd.mm.yy  HH:MM \n    Dest \n " +
                           "timing always between Source and Dest - so one of the directions is non" +
                           "-obligatory!")
    else:
        cre_msg_txt_new = ("hello " + cre_from_name + " iam a mishkas robot  **" + platform.node() + '**, ' +
                           cre_msg_txt_rule + "your original msg=" + cre_msg_txt)

    return cre_msg_txt_new


# ___________________________________________________________________________
# ___________________________________________________________________________
def main():
    running = True

    logger.info(bot)

    f_rd = chk_f_sw_i_run()
    logger.info(f_rd)


    while running:
        time.sleep(0.9)

        try:
            msg = bot.get_updates()[-1].message
            cht_id = msg.chat_id
            from_name = msg.chat["first_name"]
            msg_id = msg.message_id         # print(str(msg_id))
            msg_txt = msg.text
            skippy = False
        except telegram.error.TimedOut:
            skippy = True
            print 'Timed out, NOT logged, {:%d.%m.%Y %H:%M:%S}'.format(datetime.now())  # str(datetime.now())[0:19]
        except IndexError:
            skippy = True
            print 'Index Error: no messages on Telegram server(?). NOT logged, {:%d.%m.%Y %H:%M:%S}'.format(datetime.now())  # str(datetime.now())[0:19]
        except Exception as e:
            skippy = True
            logger.info(e)  # logger.info('   skippy True ' + str(datetime.now())[0:19])

        if (not skippy) and (msg_id > int(f_rd)):
            logger.info("cur message: msg_id=" + str(msg_id) + ", chat_id=" + str(cht_id) + ", text=" + msg_txt
                  + ", Name=" + from_name)

            msg_txt_new = cre_msg(from_name, msg_txt, cht_id)

            bot.send_message(chat_id=cht_id, text=msg_txt_new)

            upd_f_sw_i_run(msg_id, msg)
            f_rd = str(msg_id)
        # else:
        #     print(str(msg_id))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
        main()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



