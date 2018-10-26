# "D"ata "F"ile for needed "U"sage = dfu -----> strings, constants etc.

str_start = "\n\n\n * * * * * * * * * * * * START * * * * * * * * * * * * * "

str_time_out = "Timed out, NOT logged, {:%d.%m.%Y %H:%M:%S}"

str_idx_err = (
                "Index Error: no messages on Telegram "
                "server(?). NOT logged, {:%d.%m.%Y %H:%M:%S}"
                )
#
# str_rsrv_struct = (
#                     "reservation structure:\n"
#                     "Source \n"
#                     "dd.mm.yy  HH:MM \n"
#                     "Dest \n"
#                     "timing always between Source and Dest - so one of the"
#                     "directions is NON-obligatory!"
#                     )
#
# str_qstn_rule_y = (
#                     "serving  MATAF TAXI reservations, type `info` for "
#                     "reservation instructions, "
#                     )

# str_qstn_rule_gen = "type `info` for reservation instructions, `wz` to get HOME:] "

str_qstn_srch_lst = [ # 'who', 'what', 'why', 'how', 'where',
                     '.*\?', 'info', '/info', '/commands', 'commands',
                     '/help', '--help', '-help', 'help']

str_in_cmd_hom = ['/home', 'home']
str_in_cmd_wrk = ['/work', 'work']

str_out_cmnds = (
                 "<b>`work` - Calc route from home to work </b>\n"
                 "`home` - ~~ from work to HOME \n"
                 "<b>`work=RLZ, Buma Shavit 5` - set work address </b>\n"
                 "`home=TA, Hertzl 156` - set HOME address \n"
                 )

str_greeting = (
                "hello {} iam a mishkas robot  ** {} **, your "
                "msg=`{}`, type  `info`  to get commands list"
                )

str_full_tm_dist = "FROM:   {}\nTO:   {}\n*** Time: {:.0f} min ({:.0f} km)"      #%.2f

# str_is_cur_msg = "cur message: msg_id={}, chat_id={}, text={}, Name={}"

# str_wz_srch_lst = ['wz','waz','waze']

# from_address = tokenbot.from_address_main
# to_address = tokenbot.to_address_main
# region = 'IL'

