# "D"ata "F"ile for needed "U"sage = dfu -----> strings, constants etc.
import os
import json
import logging.config

def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    logger = logging.getLogger(__name__)

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger.info(str_start)                           # reference for RESTARTING..


str_start = "\n\n\n * * * * * * * * * * * * START * * * * * * * * * * * * * "



str_time_out = "Timed out, NOT logged, {:%d.%m.%Y %H:%M:%S}"

str_idx_err = (
                "Index Error: no messages on Telegram "
                "server(?). NOT logged, {:%d.%m.%Y %H:%M:%S}"
                )
lst_str_hlp_cmd = [ # 'who', 'what', 'why', 'how', 'where',
                     '.*\?', 'info', 'i', '/info', '/commands', 'commands',
                     '/help', '--help', '-help', 'help']

lst_str_hom_cmd = ['/home', 'home', 'hom', 'h']
lst_str_wrk_cmd = ['/work', 'work', 'wrk', 'w']

lst_str_upd_hom_cmd = ['home=', 'home =']
lst_str_upd_wrk_cmd = ['work=', 'work =']
lst_str_upd_nam_cmd = ['name=', 'name =']
# lst_str_to_cmd = [' to ', '--']
str_to_opr = ' to '


d_abbrv = {
            'jer': 'jerusalem',
            'ta':  'tel aviv',
            'tlv': 'tel aviv',
            'by':  'bat yam',
            'pt':  'petah tikva',
            'bs':  'beer sheva',
            'ka':  'kiryat arba',
            'ks':  'kiryat shmone',
            'ba':  'bney aysh',
            'rlz': 'rishon leziyon',
            'rg':  'ramat gan'
           }

str_out_cmnds = (
                 "<b>work</b> (Calc route from home to work)\n"
                 "<b>home</b> (.. to HOME)\n"
                 "<b>work=Ben Gurion {}, Holon</b> (set work address)\n"
                 "<b>home=haifa, Hertzl {}</b> (set HOME address)\n"
                 "<b>name=Zvika</b> (set name)\n"
                 "<b>hilel {} ramat gan to reut {} holon</b>\n"
                 "or VOICE the command !!!\n"
                 )
str_per_dtl = "\n({}) current home: {}\ncur work: {}\n"

b_s = '<b>'
b_e = '</b>'

# daily_rt_scdl_hh_str = '14'       # 15:mm   # dt_tm_~.strftime('%H:%M') ~"2018-11-07 11:57:53.238483~
dr_scdl_tm_start = [7, 40]         # 14:45
dr_scdl_tm_end = [16, 25]
# daily_rt_scdl_mm_max_str = '45'   # HH:45
#
tm_delta_hh = 0
tm_delta_mm = 0
tm_delta_ss = 25    # 1 minute(>50 sec) ==> 10%(40min)=4min --- 40>>>44min
#
rt_tm_long = 40

jmp_prc = 1.1       # 10%


str_greeting = (
                "hello {} iam a mishkas robot  **{}**, your "
                "msg=`<b>{}</b>`, type <b>info</b> to get commands list"
                )

# str_full_tm_dist = "({}) FROM:   {}\nTO:   {}\n*** Time: {:.0f} min ({:.0f} km)"      #%.2f
str_full_tm_dist = "({}) FROM:   <b>{}</b>\nTO:   <b>{}</b>"      #%.2f
