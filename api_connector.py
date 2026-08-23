
import os
import sys
import time
import json
import hmac
import hashlib
import requests
import tempfile
from urllib.parse import urlencode
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ============================================================
# MEGA-POOL FIXIE DINÁMICO DE 110 CUENTAS (HASTA 55,000 REQ/MES)
# Cuentas 11-110 (100 cuentas): NUEVAS y activas HOY con 50,000 peticiones limpias (500 c/u).
# Cuentas 1-10 (10 cuentas): Se integran automáticamente el 2 de Septiembre (+5,000 peticiones).
# ============================================================

# POOL ACTIVO DE 100 CUENTAS FIXIE (50,000 PETICIONES/MES)
FIXIE_POOL_ACTIVE_100 = [
    "http://fixie:9xFQOu1aMBiQTPF@ventoux.usefixie.com:80",   # [11] oscarhernando4@outlook.com
    "http://fixie:DKSf05uih9mtlUk@ventoux.usefixie.com:80",   # [12] oscarhernando4@gmail.com
    "http://fixie:yf5uJwPKISXERoo@ventoux.usefixie.com:80",   # [13] utn.sig@gmail.com
    "http://fixie:8Tk4o3sTwwWNzrg@ventoux.usefixie.com:80",   # [14] forestalutn@gmail.com
    "http://fixie:gKSekvjfRLL0aGz@ventoux.usefixie.com:80",   # [15] oscarhernandot11es@gmail.com
    "http://fixie:LIF3ht3W6Su0HSN@ventoux.usefixie.com:80",   # [16] oscarhernando4ec@gmail.com
    "http://fixie:yDT6fBrHaPovbZT@ventoux.usefixie.com:80",   # [17] sconcienciautn@gmail.com
    "http://fixie:RyM46ZJsdjkPpc1@ventoux.usefixie.com:80",   # [18] utn2024a@gmail.com
    "http://fixie:lMTVDtkyP9z5L3C@ventoux.usefixie.com:80",   # [19] observatorioforestalutn@gmail.com
    "http://fixie:MzJwbpHPPkPUP4n@ventoux.usefixie.com:80",   # [20] utnagp@gmail.com
    "http://fixie:N8Q2thJQNHQ3z7X@ventoux.usefixie.com:80",   # [21] dronforestalutn@gmail.com
    "http://fixie:QPG9Y4o5bzzgQMB@ventoux.usefixie.com:80",   # [22] oscarhernando4@outlook.com
    "http://fixie:4dmxiL6T14QDrCU@ventoux.usefixie.com:80",   # [23] oscarhernando4@outlook.com v3
    "http://fixie:8AtYO51OoEFRo0f@ventoux.usefixie.com:80",   # [24] oscarhernando4@gmail.com v3
    "http://fixie:FSytVSP03izcAVP@ventoux.usefixie.com:80",   # [25] utn.sig@gmail.com v3
    "http://fixie:PuQ03wtaIPgSBH1@ventoux.usefixie.com:80",   # [26] forestalutn@gmail.com v3
    "http://fixie:u92WjCG7m69dHA5@ventoux.usefixie.com:80",   # [27] oscarhernandot11es@gmail.com v3
    "http://fixie:8vBYarKudfOmzF3@ventoux.usefixie.com:80",   # [28] oscarhernando4ec@gmail.com V3
    "http://fixie:NgudJ1GXr9ieiQX@ventoux.usefixie.com:80",   # [29] sconcienciautn@gmail.com V3
    "http://fixie:7loizt3CZ3jUPhF@ventoux.usefixie.com:80",   # [30] utn2024a@gmail.com V3
    "http://fixie:MUWNFEVfZaUNmJa@ventoux.usefixie.com:80",   # [31] observatorioforestalutn@gmail.com V3
    "http://fixie:knXCZulVWM5k0VE@ventoux.usefixie.com:80",   # [32] utnagp@gmail.com V3
    "http://fixie:VKyAMpwQRjqrrYC@ventoux.usefixie.com:80",   # [33] dronforestalutn@gmail.com V3
    "http://fixie:SlL5HdagGw0byiw@ventoux.usefixie.com:80",   # [34] oscarhernando4@outlook.com V4
    "http://fixie:aPQ5bGoNrGMaBQv@ventoux.usefixie.com:80",   # [35] oscarhernando4@outlook.com V5
    "http://fixie:s5ujI6Bt1sdFkoi@ventoux.usefixie.com:80",   # [36] oscarhernando4@outlook.com V6
    "http://fixie:3QFYO7P7RvZfSwE@ventoux.usefixie.com:80",   # [37] oscarhernando4@outlook.com V7
    "http://fixie:YAEqGbRkdbJF1xc@ventoux.usefixie.com:80",   # [38] oscarhernando4@outlook.com V8
    "http://fixie:Tzt082RmWVjmq3h@ventoux.usefixie.com:80",   # [39] oscarhernando4@outlook.com V9
    "http://fixie:X12q3RXyEFDjyLi@ventoux.usefixie.com:80",   # [40] oscarhernando4@outlook.com V10
    "http://fixie:QfGXr1jMNMHfreR@ventoux.usefixie.com:80",   # [41] oscarhernando4@gmail.com V4
    "http://fixie:mXm0pZ7raygtMbS@ventoux.usefixie.com:80",   # [42] oscarhernando4@gmail.com V5
    "http://fixie:4DhMVGlEAwsrWjy@ventoux.usefixie.com:80",   # [43] oscarhernando4@gmail.com V6
    "http://fixie:nYCWFS4P2w1NmuA@ventoux.usefixie.com:80",   # [44] oscarhernando4@gmail.com V7
    "http://fixie:7vcJzgGFyqRp1JZ@ventoux.usefixie.com:80",   # [45] oscarhernando4@gmail.com V8
    "http://fixie:JzaNxHMbT6lDbeO@ventoux.usefixie.com:80",   # [46] oscarhernando4@gmail.com V9
    "http://fixie:s9Am4KgrKvnC4Lp@ventoux.usefixie.com:80",   # [47] oscarhernando4@gmail.com V10
    "http://fixie:TbQs1jiB5DX3Ck2@ventoux.usefixie.com:80",   # [48] utn.sig@gmail.com V4
    "http://fixie:tujOpotr8B9lFmS@ventoux.usefixie.com:80",   # [49] utn.sig@gmail.com V5
    "http://fixie:EMbi6wqyJt133y2@ventoux.usefixie.com:80",   # [50] utn.sig@gmail.com V6
    "http://fixie:sAYyvrw2Z1pYuYd@ventoux.usefixie.com:80",   # [51] utn.sig@gmail.com V7
    "http://fixie:PonwpNOqHbW8KTU@ventoux.usefixie.com:80",   # [52] utn.sig@gmail.com V8
    "http://fixie:wrNjVWjGpN0FtDg@ventoux.usefixie.com:80",   # [53] utn.sig@gmail.com V9
    "http://fixie:VvRuxBU3YlBHDOu@ventoux.usefixie.com:80",   # [54] utn.sig@gmail.com V10
    "http://fixie:of87MTT1vKk9VZE@ventoux.usefixie.com:80",   # [55] forestalutn@gmail.com V4
    "http://fixie:TopFxImxU2kBwRb@ventoux.usefixie.com:80",   # [56] forestalutn@gmail.com V5
    "http://fixie:7pseBSFfWAIn4cE@ventoux.usefixie.com:80",   # [57] forestalutn@gmail.com V6
    "http://fixie:dNHCOhJgXWNuEpb@ventoux.usefixie.com:80",   # [58] forestalutn@gmail.com V7
    "http://fixie:QmmXmlwFyoWljxt@ventoux.usefixie.com:80",   # [59] forestalutn@gmail.com V8
    "http://fixie:JR51qhrugxAyUrv@ventoux.usefixie.com:80",   # [60] forestalutn@gmail.com V9
    "http://fixie:nbbEI7WLkZqOABq@ventoux.usefixie.com:80",   # [61] forestalutn@gmail.com V10
    "http://fixie:OlCBNNigi0jlSzq@ventoux.usefixie.com:80",   # [62] oscarhernandot11es@gmail.com V4
    "http://fixie:tyfFexDViWW9EdJ@ventoux.usefixie.com:80",   # [63] oscarhernandot11es@gmail.com V5
    "http://fixie:iXf3ZBUTst5sQI8@ventoux.usefixie.com:80",   # [64] oscarhernandot11es@gmail.com V6
    "http://fixie:R5re8pwPrUWMMRH@ventoux.usefixie.com:80",   # [65] oscarhernandot11es@gmail.com V7
    "http://fixie:9Bjb1RDuNbl9aPN@ventoux.usefixie.com:80",   # [66] oscarhernandot11es@gmail.com V8
    "http://fixie:2dzTvtRV5zzsE3H@ventoux.usefixie.com:80",   # [67] oscarhernandot11es@gmail.com V9
    "http://fixie:KXMQryFsT15FYG0@ventoux.usefixie.com:80",   # [68] oscarhernandot11es@gmail.com V10
    "http://fixie:TE959r3guJd6MNH@ventoux.usefixie.com:80",   # [69] oscarhernando4ec@gmail.com V4
    "http://fixie:rIymdfiB2mGLnsh@ventoux.usefixie.com:80",   # [70] oscarhernando4ec@gmail.com V5
    "http://fixie:zMuLwhByrapBn0p@ventoux.usefixie.com:80",   # [71] oscarhernando4ec@gmail.com V6
    "http://fixie:JuHWvIE7c6UuTgU@ventoux.usefixie.com:80",   # [72] oscarhernando4ec@gmail.com V7
    "http://fixie:hqoh6jFi87Msju6@ventoux.usefixie.com:80",   # [73] oscarhernando4ec@gmail.com V8
    "http://fixie:TGCu9JxgluBKrXG@ventoux.usefixie.com:80",   # [74] oscarhernando4ec@gmail.com V9
    "http://fixie:4sBk6tCzQxYVAnp@ventoux.usefixie.com:80",   # [75] oscarhernando4ec@gmail.com V10
    "http://fixie:SCKlgu158eTDESE@ventoux.usefixie.com:80",   # [76] sconcienciautn@gmail.com V4
    "http://fixie:c2n0JOjKOH6BtHZ@ventoux.usefixie.com:80",   # [77] sconcienciautn@gmail.com V5
    "http://fixie:lVBepd02P78PKa7@ventoux.usefixie.com:80",   # [78] sconcienciautn@gmail.com V6
    "http://fixie:0zSa5YgvhNHvB4c@ventoux.usefixie.com:80",   # [79] sconcienciautn@gmail.com V7
    "http://fixie:twlErm51o6cSMSj@ventoux.usefixie.com:80",   # [80] sconcienciautn@gmail.com V8
    "http://fixie:6X4EuzNoxY1rMCR@ventoux.usefixie.com:80",   # [81] sconcienciautn@gmail.com V9
    "http://fixie:lT7M8teKC2O4CHO@ventoux.usefixie.com:80",   # [82] sconcienciautn@gmail.com V10
    "http://fixie:Apa00rv3GvDPtuU@ventoux.usefixie.com:80",   # [83] utn2024a@gmail.com V4
    "http://fixie:98AmV4aWdS94zKW@ventoux.usefixie.com:80",   # [84] utn2024a@gmail.com V5
    "http://fixie:rTaZ4OoGypA7FtJ@ventoux.usefixie.com:80",   # [85] utn2024a@gmail.com V6
    "http://fixie:jG7Y64tpC61l1XR@ventoux.usefixie.com:80",   # [86] utn2024a@gmail.com V7
    "http://fixie:6n2ETd69fOuQDwb@ventoux.usefixie.com:80",   # [87] utn2024a@gmail.com V8
    "http://fixie:g2m2HQuEw3r8XGA@ventoux.usefixie.com:80",   # [88] utn2024a@gmail.com V9
    "http://fixie:3HKojEzIFPjXdWu@ventoux.usefixie.com:80",   # [89] utn2024a@gmail.com V10
    "http://fixie:ihFw1MEyw67j4Sb@ventoux.usefixie.com:80",   # [90] observatorioforestalutn@gmail.com V4
    "http://fixie:xTjAESW0BCuXYRT@ventoux.usefixie.com:80",   # [91] observatorioforestalutn@gmail.com V5
    "http://fixie:16RZbIbGND7Upa7@ventoux.usefixie.com:80",   # [92] observatorioforestalutn@gmail.com V6
    "http://fixie:Fr1czdAIrtazgSa@ventoux.usefixie.com:80",   # [93] observatorioforestalutn@gmail.com V7
    "http://fixie:W539B33fqP0NeoO@ventoux.usefixie.com:80",   # [94] observatorioforestalutn@gmail.com V8
    "http://fixie:8aMbL796jGzEvYY@ventoux.usefixie.com:80",   # [95] observatorioforestalutn@gmail.com V9
    "http://fixie:FwVgD9z373Bf8So@ventoux.usefixie.com:80",   # [96] observatorioforestalutn@gmail.com V10
    "http://fixie:AHLdbG345IhRCX8@ventoux.usefixie.com:80",   # [97] utnagp@gmail.com V4
    "http://fixie:66Krdxu7COau0tl@ventoux.usefixie.com:80",   # [98] utnagp@gmail.com V5
    "http://fixie:WdoiyEBCAkGqV2y@ventoux.usefixie.com:80",   # [99] utnagp@gmail.com V6
    "http://fixie:MpAgavL7JY8eTzc@ventoux.usefixie.com:80",   # [100] utnagp@gmail.com V7
    "http://fixie:ss2BY11b67SoTJw@ventoux.usefixie.com:80",   # [101] utnagp@gmail.com V8
    "http://fixie:U1juZsE977WMFa2@ventoux.usefixie.com:80",   # [102] utnagp@gmail.com V9
    "http://fixie:yn6Vre4nVz0o6ai@ventoux.usefixie.com:80",   # [103] utnagp@gmail.com V10
    "http://fixie:rdVhxQRBYIZBFhd@ventoux.usefixie.com:80",   # [104] dronforestalutn@gmail.com V4
    "http://fixie:ycuo8c76hn2NFyX@ventoux.usefixie.com:80",   # [105] dronforestalutn@gmail.com V5
    "http://fixie:cgkrvkO9VOAL2QO@ventoux.usefixie.com:80",   # [106] dronforestalutn@gmail.com V6
    "http://fixie:G9uoaEDykw9G0zL@ventoux.usefixie.com:80",   # [107] dronforestalutn@gmail.com V7
    "http://fixie:pTkcVI1KumODv7q@ventoux.usefixie.com:80",   # [108] dronforestalutn@gmail.com V8
    "http://fixie:2jegAv8VundxGI3@ventoux.usefixie.com:80",   # [109] dronforestalutn@gmail.com V9
    "http://fixie:TXQSQqu0lQVe3xY@ventoux.usefixie.com:80",   # [110] dronforestalutn@gmail.com V10
]

FIXIE_ACCOUNTS_ACTIVE_100 = [
    "fixie_011_oscarhernando4_outlook_com",
    "fixie_012_oscarhernando4_gmail_com",
    "fixie_013_utn_sig_gmail_com",
    "fixie_014_forestalutn_gmail_com",
    "fixie_015_oscarhernandot11es_gmail_com",
    "fixie_016_oscarhernando4ec_gmail_com",
    "fixie_017_sconcienciautn_gmail_com",
    "fixie_018_utn2024a_gmail_com",
    "fixie_019_observatorioforestalutn_gmail_com",
    "fixie_020_utnagp_gmail_com",
    "fixie_021_dronforestalutn_gmail_com",
    "fixie_022_oscarhernando4_outlook_com",
    "fixie_023_oscarhernando4_outlook_com_v3",
    "fixie_024_oscarhernando4_gmail_com_v3",
    "fixie_025_utn_sig_gmail_com_v3",
    "fixie_026_forestalutn_gmail_com_v3",
    "fixie_027_oscarhernandot11es_gmail_com_v3",
    "fixie_028_oscarhernando4ec_gmail_com_V3",
    "fixie_029_sconcienciautn_gmail_com_V3",
    "fixie_030_utn2024a_gmail_com_V3",
    "fixie_031_observatorioforestalutn_gmail_com_V3",
    "fixie_032_utnagp_gmail_com_V3",
    "fixie_033_dronforestalutn_gmail_com_V3",
    "fixie_034_oscarhernando4_outlook_com_V4",
    "fixie_035_oscarhernando4_outlook_com_V5",
    "fixie_036_oscarhernando4_outlook_com_V6",
    "fixie_037_oscarhernando4_outlook_com_V7",
    "fixie_038_oscarhernando4_outlook_com_V8",
    "fixie_039_oscarhernando4_outlook_com_V9",
    "fixie_040_oscarhernando4_outlook_com_V10",
    "fixie_041_oscarhernando4_gmail_com_V4",
    "fixie_042_oscarhernando4_gmail_com_V5",
    "fixie_043_oscarhernando4_gmail_com_V6",
    "fixie_044_oscarhernando4_gmail_com_V7",
    "fixie_045_oscarhernando4_gmail_com_V8",
    "fixie_046_oscarhernando4_gmail_com_V9",
    "fixie_047_oscarhernando4_gmail_com_V10",
    "fixie_048_utn_sig_gmail_com_V4",
    "fixie_049_utn_sig_gmail_com_V5",
    "fixie_050_utn_sig_gmail_com_V6",
    "fixie_051_utn_sig_gmail_com_V7",
    "fixie_052_utn_sig_gmail_com_V8",
    "fixie_053_utn_sig_gmail_com_V9",
    "fixie_054_utn_sig_gmail_com_V10",
    "fixie_055_forestalutn_gmail_com_V4",
    "fixie_056_forestalutn_gmail_com_V5",
    "fixie_057_forestalutn_gmail_com_V6",
    "fixie_058_forestalutn_gmail_com_V7",
    "fixie_059_forestalutn_gmail_com_V8",
    "fixie_060_forestalutn_gmail_com_V9",
    "fixie_061_forestalutn_gmail_com_V10",
    "fixie_062_oscarhernandot11es_gmail_com_V4",
    "fixie_063_oscarhernandot11es_gmail_com_V5",
    "fixie_064_oscarhernandot11es_gmail_com_V6",
    "fixie_065_oscarhernandot11es_gmail_com_V7",
    "fixie_066_oscarhernandot11es_gmail_com_V8",
    "fixie_067_oscarhernandot11es_gmail_com_V9",
    "fixie_068_oscarhernandot11es_gmail_com_V10",
    "fixie_069_oscarhernando4ec_gmail_com_V4",
    "fixie_070_oscarhernando4ec_gmail_com_V5",
    "fixie_071_oscarhernando4ec_gmail_com_V6",
    "fixie_072_oscarhernando4ec_gmail_com_V7",
    "fixie_073_oscarhernando4ec_gmail_com_V8",
    "fixie_074_oscarhernando4ec_gmail_com_V9",
    "fixie_075_oscarhernando4ec_gmail_com_V10",
    "fixie_076_sconcienciautn_gmail_com_V4",
    "fixie_077_sconcienciautn_gmail_com_V5",
    "fixie_078_sconcienciautn_gmail_com_V6",
    "fixie_079_sconcienciautn_gmail_com_V7",
    "fixie_080_sconcienciautn_gmail_com_V8",
    "fixie_081_sconcienciautn_gmail_com_V9",
    "fixie_082_sconcienciautn_gmail_com_V10",
    "fixie_083_utn2024a_gmail_com_V4",
    "fixie_084_utn2024a_gmail_com_V5",
    "fixie_085_utn2024a_gmail_com_V6",
    "fixie_086_utn2024a_gmail_com_V7",
    "fixie_087_utn2024a_gmail_com_V8",
    "fixie_088_utn2024a_gmail_com_V9",
    "fixie_089_utn2024a_gmail_com_V10",
    "fixie_090_observatorioforestalutn_gmail_com_V4",
    "fixie_091_observatorioforestalutn_gmail_com_V5",
    "fixie_092_observatorioforestalutn_gmail_com_V6",
    "fixie_093_observatorioforestalutn_gmail_com_V7",
    "fixie_094_observatorioforestalutn_gmail_com_V8",
    "fixie_095_observatorioforestalutn_gmail_com_V9",
    "fixie_096_observatorioforestalutn_gmail_com_V10",
    "fixie_097_utnagp_gmail_com_V4",
    "fixie_098_utnagp_gmail_com_V5",
    "fixie_099_utnagp_gmail_com_V6",
    "fixie_100_utnagp_gmail_com_V7",
    "fixie_101_utnagp_gmail_com_V8",
    "fixie_102_utnagp_gmail_com_V9",
    "fixie_103_utnagp_gmail_com_V10",
    "fixie_104_dronforestalutn_gmail_com_V4",
    "fixie_105_dronforestalutn_gmail_com_V5",
    "fixie_106_dronforestalutn_gmail_com_V6",
    "fixie_107_dronforestalutn_gmail_com_V7",
    "fixie_108_dronforestalutn_gmail_com_V8",
    "fixie_109_dronforestalutn_gmail_com_V9",
    "fixie_110_dronforestalutn_gmail_com_V10",
]

# POOL DE LAS 10 CUENTAS QUE SE REACTIVAN EL 2 DE SEPTIEMBRE (+5,000 PETICIONES/MES)
FIXIE_POOL_SEPT2_10 = [
    "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80",   # [1] oscarhernando4@gmail.com
    "http://fixie:ak4QPysr5gnUAQW@ventoux.usefixie.com:80",   # [2] utn.sig@gmail.com
    "http://fixie:ygTezfOLKeqEhhF@ventoux.usefixie.com:80",   # [3] forestalutn@gmail.com
    "http://fixie:zW3cwceDZ64c1lE@ventoux.usefixie.com:80",   # [4] oscarhernandot11es@gmail.com
    "http://fixie:SIOQ4x5oF0pbFju@ventoux.usefixie.com:80",   # [5] oscarhernando4ec@gmail.com
    "http://fixie:V9uciGagtBF2MJc@ventoux.usefixie.com:80",   # [6] sconcienciautn@gmail.com
    "http://fixie:gnvJakG6jyBrS04@ventoux.usefixie.com:80",   # [7] utn2024a@gmail.com
    "http://fixie:YOtqrUO1HVYG2xM@ventoux.usefixie.com:80",   # [8] observatorioforestalutn@gmail.com
    "http://fixie:WWaxRExXfmPL05s@ventoux.usefixie.com:80",   # [9] utnagp@gmail.com
    "http://fixie:f9ibnMDQHLjZTpM@ventoux.usefixie.com:80",   # [10] dronforestalutn@gmail.com
]

FIXIE_ACCOUNTS_SEPT2_10 = [
    "fixie_001_oscarhernando4_gmail_com",
    "fixie_002_utn_sig_gmail_com",
    "fixie_003_forestalutn_gmail_com",
    "fixie_004_oscarhernandot11es_gmail_com",
    "fixie_005_oscarhernando4ec_gmail_com",
    "fixie_006_sconcienciautn_gmail_com",
    "fixie_007_utn2024a_gmail_com",
    "fixie_008_observatorioforestalutn_gmail_com",
    "fixie_009_utnagp_gmail_com",
    "fixie_010_dronforestalutn_gmail_com",
]

def get_active_fixie_pool_and_accounts():
    """Retorna el pool activo: 100 cuentas nuevas hoy (50,000 req), o 110 cuentas a partir del 2 de Septiembre (55,000 req)."""
    now = datetime.now()
    if now.year > 2026 or (now.year == 2026 and (now.month > 9 or (now.month == 9 and now.day >= 2))):
        return FIXIE_POOL_ACTIVE_100 + FIXIE_POOL_SEPT2_10, FIXIE_ACCOUNTS_ACTIVE_100 + FIXIE_ACCOUNTS_SEPT2_10
    return FIXIE_POOL_ACTIVE_100, FIXIE_ACCOUNTS_ACTIVE_100

FIXIE_POOL, FIXIE_ACCOUNTS = get_active_fixie_pool_and_accounts()


# ============================================================
# SISTEMA HÍBRIDO LOCAL/NUBE + ROUND-ROBIN EQUITATIVO
# ============================================================
PROXY_STATE_FILE = os.path.join(os.path.dirname(__file__), "proxy_state.json")
EXECUTION_MODE_FILE = os.path.join(os.path.dirname(__file__), "execution_mode.json")

def _load_proxy_state():
    """Carga el estado persistente del rotador de proxies."""
    try:
        with open(PROXY_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_index": 0, "usage": {}}

def _save_proxy_state(state):
    """Guarda el estado del rotador de proxies."""
    try:
        with open(PROXY_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def get_execution_mode():
    """Lee el modo de ejecución actual: 'local' o 'cloud'."""
    try:
        with open(EXECUTION_MODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("mode", "cloud")
    except Exception:
        return "cloud"

def set_execution_mode(mode):
    """Cambia entre 'local' (sin proxy) y 'cloud' (con Fixie)."""
    data = {
        "mode": mode,
        "switched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "switched_by": "api_connector"
    }
    try:
        with open(EXECUTION_MODE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    emoji = "🖥️ LOCAL (Sin Proxy)" if mode == "local" else "☁️ NUBE (Fixie Proxy)"
    print(f"🔄 Modo de ejecución cambiado a: {emoji}")

def get_proxy():
    """Round-Robin equitativo: rota secuencialmente entre cuentas Fixie activas con auto-renovación mensual."""
    state = _load_proxy_state()
    idx = state.get("current_index", 9) % len(FIXIE_POOL)
    
    # Dynamic exhausted accounts (auto-clears on monthly renewal)
    exhausted = state.get("exhausted", {})
    current_month = datetime.now().strftime("%Y-%m")
    
    # Auto-renewal: if the month changed since last exhaustion, clear ALL exhausted flags
    last_exhaust_month = state.get("last_exhaust_month", "")
    if current_month != last_exhaust_month and exhausted:
        print(f"🔄 [FIXIE AUTO-RENOVACIÓN] Nuevo mes detectado ({current_month}). Reactivando las {len(exhausted)} cuentas Fixie pausadas.")
        exhausted = {}
        state["exhausted"] = {}
        state["last_exhaust_month"] = current_month
        _save_proxy_state(state)
    
    exhausted_indices = set(exhausted.get("indices", []))
    
    # Find next available account
    attempts = 0
    while idx in exhausted_indices and attempts < len(FIXIE_POOL):
        idx = (idx + 1) % len(FIXIE_POOL)
        attempts += 1
    
    # If ALL accounts exhausted, force reset (emergency fallback)
    if attempts >= len(FIXIE_POOL):
        print("⚠️ [FIXIE] TODAS las cuentas agotadas. Forzando reset de emergencia...")
        exhausted_indices = set()
        state["exhausted"] = {}
        idx = 9  # Start from primary account
        
    url = FIXIE_POOL[idx]
    
    # Advance to next for next call
    state["current_index"] = (idx + 1) % len(FIXIE_POOL)
    
    # Usage tracking per account
    usage = state.setdefault("usage", {})
    account_name = FIXIE_ACCOUNTS[idx]
    usage[account_name] = usage.get(account_name, 0) + 1
    state["last_used"] = account_name
    state["last_used_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    _save_proxy_state(state)
    return {"http": url, "https": url}

def mark_fixie_exhausted(account_index):
    """Marks a Fixie account as exhausted (quota depleted). Auto-clears on monthly renewal."""
    state = _load_proxy_state()
    exhausted = state.setdefault("exhausted", {})
    indices = exhausted.setdefault("indices", [])
    if account_index not in indices:
        indices.append(account_index)
        state["last_exhaust_month"] = datetime.now().strftime("%Y-%m")
        _save_proxy_state(state)
        name = FIXIE_ACCOUNTS[account_index] if account_index < len(FIXIE_ACCOUNTS) else f"#{account_index}"
        print(f"🚫 [FIXIE] Cuenta {name} marcada como agotada. Activas: {len(FIXIE_POOL) - len(indices)}/{len(FIXIE_POOL)}")

def get_smart_proxy():
    """Proxy inteligente: usa directo si modo local, Fixie Round-Robin si modo nube."""
    if get_execution_mode() == "local":
        return None  # Sin proxy = conexión directa desde PC
    return get_proxy()  # Round-Robin Fixie equitativo

# Legacy compatibility (solo para imports externos)
PROXY_URL = FIXIE_POOL[0]
PROXIES = None  # Lazy: use get_smart_proxy() per-request instead of wasting Fixie quota on module reload

def get_api_key():
    return os.getenv("BINANCE_REAL_API_KEY", "").strip()

def get_api_secret():
    return os.getenv("BINANCE_REAL_API_SECRET", "").strip()

API_KEY = get_api_key()
API_SECRET = get_api_secret()
BASE_URL = "https://api.binance.com"
FAPI_URL = "https://fapi.binance.com"

REAL_STATE_FILE = os.path.join(os.path.dirname(__file__), "real_money_account.json")

# ============================================================
# STATE MANAGEMENT (Atomic writes to prevent corruption)
# ============================================================

def load_real_account_state():
    if os.path.exists(REAL_STATE_FILE):
        try:
            with open(REAL_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Ensure all required keys exist with safe defaults
                state.setdefault("initial_deposit_usdt", 15.47)
                state.setdefault("initial_total_usd", 20.07)
                state.setdefault("current_balance_usd", 20.07)
                state.setdefault("net_pnl_usd", 0.0)
                state.setdefault("wins", 0)
                state.setdefault("losses", 0)
                state.setdefault("trades_count", 0)
                state.setdefault("daily_wins", 0)
                state.setdefault("daily_losses", 0)
                state.setdefault("position", None)
                state.setdefault("last_trade_time", datetime.now().strftime("%y-%m-%d<br>%H:%M"))
                state.setdefault("status", "🟦 Buscando Entrada A+")
                return state
        except Exception:
            pass
    return {
        "initial_deposit_usdt": 15.47,
        "initial_total_usd": 20.07,
        "current_balance_usd": 20.07,
        "net_pnl_usd": 0.0,
        "wins": 0,
        "losses": 0,
        "trades_count": 0,
        "daily_wins": 0,
        "daily_losses": 0,
        "position": None,
        "last_trade_time": datetime.now().strftime("%y-%m-%d<br>%H:%M"),
        "status": "🟦 Buscando Entrada A+"
    }

def save_real_account_state(state):
    """Atomic write: write to temp file first, then rename to prevent corruption."""
    dir_path = os.path.dirname(REAL_STATE_FILE)
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=dir_path)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        # Atomic rename (on same filesystem)
        if os.path.exists(REAL_STATE_FILE):
            os.replace(tmp_path, REAL_STATE_FILE)
        else:
            os.rename(tmp_path, REAL_STATE_FILE)
    except Exception:
        # Fallback to direct write if atomic fails
        with open(REAL_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

# ============================================================
# BALANCE & POSITION QUERIES (NO Fixie proxy - free API calls)
# ============================================================

def get_real_balances():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=6)
        if res.status_code == 200:
            return res.json().get("balances", [])
    except Exception:
        pass
        
    # Direct Connection Fallback for Local PC
    try:
        res = requests.get(url, headers=headers, params=params, proxies=None, timeout=6)
        if res.status_code == 200:
            return res.json().get("balances", [])
    except Exception:
        pass
    return None

def get_real_usdt_balance():
    balances = get_real_balances()
    if not balances:
        return 0.0
    return sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])

def get_real_futures_balances():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{FAPI_URL}/fapi/v2/account"
    try:
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        if res.status_code == 200:
            return res.json().get("assets", [])
        return None
    except Exception:
        return None

def get_real_futures_positions():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{FAPI_URL}/fapi/v2/positionRisk"
    try:
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        if res.status_code == 200:
            positions = res.json()
            return [p for p in positions if float(p.get("positionAmt", 0)) != 0.0]
        return []
    except Exception:
        return []

def get_real_futures_usdt_balance():
    assets = get_real_futures_balances()
    if not assets:
        return 0.0
    return sum([float(a["availableBalance"]) for a in assets if a["asset"] in ["USDT", "USDC"]])

def get_symbol_price(symbol, is_futures=False):
    """
    Ultra-resilient live price fetcher with multiple fallback mirrors and proxy backup.
    """
    endpoints = [
        f"https://data-api.binance.vision/api/v3/ticker/price?symbol={symbol}",
        f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api2.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api3.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    ]
    
    for url in endpoints:
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            if res.status_code == 200:
                p = float(res.json().get("price", 0))
                if p > 0:
                    return p
        except Exception:
            continue
            
    return None

def get_recent_kline_high(symbol, limit=5, start_time_ms=None):
    """
    Fetches the highest price peak (High wick) from recent 1-minute klines AFTER position entry.
    Uses 100% public high-throughput endpoints with 0 Fixie proxy consumption.
    """
    mirrors = [
        "https://data-api.binance.vision/api/v3/klines",
        "https://api1.binance.com/api/v3/klines",
        "https://api2.binance.com/api/v3/klines",
        "https://api3.binance.com/api/v3/klines",
        "https://api.binance.com/api/v3/klines"
    ]
    params = {"symbol": symbol, "interval": "1m", "limit": limit}
    if start_time_ms and start_time_ms > 0:
        params["startTime"] = int(start_time_ms)
    
    for url in mirrors:
        try:
            res = requests.get(url, params=params, timeout=3)
            if res.status_code == 200:
                k_data = res.json()
                if isinstance(k_data, list) and len(k_data) > 0:
                    if start_time_ms and start_time_ms > 0:
                        filtered = [k for k in k_data if int(k[0]) >= int(start_time_ms)]
                        if filtered:
                            return max([float(k[2]) for k in filtered])
                        return 0.0
                    return max([float(k[2]) for k in k_data])
        except Exception:
            continue
            
    return 0.0

# ============================================================
# ORDER EXECUTION (Uses Fixie proxy - counted towards quota)
# ============================================================

def execute_real_spot_market_buy(symbol, usdt_amount):
    """
    Executes a SPOT MARKET BUY using quoteOrderQty (100% free USDT).
    Uses 30-Minute Smart Balance Cache to conserve Fixie proxy requests (~0 extra API calls).
    """
    import math
    timestamp = int(time.time() * 1000)
    state = load_real_account_state()
    
    # Read cached USDT balance from 30m diagnosis state (zero Fixie proxy requests consumed)
    cached_usdt = state.get("_cached_usdt_free", 0.0)
    if cached_usdt > 0:
        usdt_amount = min(usdt_amount, cached_usdt)
        
    clean_usd = math.floor(usdt_amount * 10) / 10.0
    if clean_usd < 5.1:
        return {"error": f"MIN_NOTIONAL not met (${clean_usd:.1f} < $5.10)"}
        
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{clean_usd:.1f}",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    api_k = get_api_key()
    api_s = get_api_secret()
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE OPENED] Sincronizando balance real desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after buy: {se}")
        return res_json
    except Exception as e:
        print(f"⚠️ [API RETRY] Error en proxy ({e}). Reintentando compra Spot vía conexión directa...")
        try:
            res = requests.post(url, headers=headers, params=params, proxies=None, timeout=10)
            res_json = res.json()
            if "orderId" in res_json or res_json.get("status") == "FILLED":
                try:
                    diagnose_full_spot_wallet()
                except Exception:
                    pass
            return res_json
        except Exception as e2:
            return {"error": str(e2)}

def execute_real_spot_market_sell(symbol, quantity=None):
    """
    Executes a SPOT MARKET SELL.
    - If quantity is None, fetches the entire free balance of the asset.
    - Dynamically gets LOT_SIZE and stepSize precision to prevent API rejects.
    """
    import math
    asset = symbol.replace("USDT", "")
    
    if quantity is None:
        balances = get_real_balances()
        if balances:
            for b in balances:
                if b.get("asset") == asset:
                    quantity = float(b.get("free", 0))
                    break
                    
    if not quantity or quantity <= 0:
        return {"error": f"No available balance to sell for {symbol}"}
        
    try:
        ex_info = requests.get(f"{BASE_URL}/api/v3/exchangeInfo?symbol={symbol}", proxies=get_smart_proxy(), timeout=5).json()
        symbol_info = ex_info.get("symbols", [{}])[0]
        step_size = 0.01
        qty_precision = 2
        for f in symbol_info.get("filters", []):
            if f.get("filterType") == "LOT_SIZE":
                step_size = float(f.get("stepSize", "0.01"))
                if "." in f.get("stepSize", ""):
                    qty_precision = len(f.get("stepSize", "").split(".")[1].rstrip("0"))
                else:
                    qty_precision = 0
                break
    except Exception as e:
        print(f"Error fetching precision for {symbol}, defaulting: {e}")
        qty_precision = 2
        step_size = 0.01
        
    if step_size < 1.0 and qty_precision > 0:
        quantized_qty = math.floor(quantity / step_size) * step_size
        qty_str = f"{quantized_qty:.{qty_precision}f}"
    else:
        qty_str = str(int(math.floor(quantity)))
        
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
        "timestamp": int(time.time() * 1000)
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE CLOSED] Sincronizando balance real en vivo desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after sell: {se}")
        return res_json
    except Exception as e:
        print(f"⚠️ [API RETRY] Error en proxy ({e}). Reintentando venta Spot vía conexión directa...")
        try:
            res = requests.post(url, headers=headers, params=params, proxies=None, timeout=10)
            res_json = res.json()
            if "orderId" in res_json or res_json.get("status") == "FILLED":
                try:
                    diagnose_full_spot_wallet()
                except Exception:
                    pass
            return res_json
        except Exception as e2:
            return {"error": str(e2)}

def get_exact_real_entry_price(symbol):
    """
    Queries Binance /api/v3/myTrades to extract the exact weighted average fill price
    for the most recent BUY order of the specified symbol.
    """
    try:
        api_k = get_api_key()
        api_s = get_api_secret()
        ts = int(time.time() * 1000)
        params = {"symbol": symbol, "timestamp": ts, "limit": 10}
        qs = urlencode(params)
        sig = hmac.new(api_s.encode("utf-8"), qs.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = sig
        headers = {"X-MBX-APIKEY": api_k}
        
        url = f"{BASE_URL}/api/v3/myTrades"
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=5)
        trades = res.json()
        if isinstance(trades, list) and trades:
            buy_trades = [t for t in trades if t.get("isBuyer", False)]
            if buy_trades:
                last_order_id = buy_trades[-1].get("orderId")
                matching_fills = [t for t in buy_trades if t.get("orderId") == last_order_id]
                total_qty = sum(float(t["qty"]) for t in matching_fills)
                total_cost = sum(float(t["quoteQty"]) for t in matching_fills)
                if total_qty > 0 and total_cost > 0:
                    return round(total_cost / total_qty, 8), round(total_cost, 2), round(total_qty, 4)
    except Exception as e:
        print(f"Error fetching exact trades for {symbol}: {e}")
    return None, None, None

def diagnose_full_spot_wallet():
    """
    60-MINUTE COMPREHENSIVE SPOT WALLET DIAGNOSIS (via Fixie Proxy).
    Runs every 60 minutes to conserve Fixie proxy requests (~24 req/day).
    - Inspects ALL assets held in Spot (USDT, BNB, and active cryptos).
    - Computes exact USD value for every coin.
    - Auto-detects and adopts active positions (> $5 USD) using EXACT fill prices from myTrades.
    - Auto-clears positions if coin was manually sold/converted.
    - Updates real_money_account.json state.
    """
    state = load_real_account_state()
    balances = get_real_balances()
    if not balances:
        print("⚠️ [DIAGNÓSTICO] No se pudieron obtener los balances desde Binance API.")
        return state
        
    usdt_free = 0.0
    bnb_free = 0.0
    bnb_usd = 0.0
    total_wallet_usd = 0.0
    crypto_holdings = []
    
    # Fetch BNB price for fee shield calculation
    bnb_price = get_symbol_price("BNBUSDT", is_futures=False) or 575.0
    
    stablecoin_set = {
        "USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "RLUSD", "USD1",
        "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD"
    }
    
    print("\n" + "="*60)
    print("🔍 [DIAGNÓSTICO INTEGRAL DE BILLETERA SPOT (FIXIE 60-MIN / EVENTO)]")
    print("="*60)
    
    for b in balances:
        asset = b.get("asset", "")
        free_qty = float(b.get("free", 0))
        locked_qty = float(b.get("locked", 0))
        total_qty = free_qty + locked_qty
        
        if total_qty <= 0.000001:
            continue
            
        if asset == "USDT":
            usdt_free = free_qty
            total_wallet_usd += free_qty
            print(f"  💵 USDT Disponible: ${free_qty:.4f} USDT")
        elif asset == "BNB":
            bnb_free = free_qty
            bnb_usd = free_qty * bnb_price
            total_wallet_usd += bnb_usd
            print(f"  🟡 BNB Escudo Comisiones: {free_qty:.6f} BNB (~${bnb_usd:.2f} USD @ ${bnb_price:.2f})")
        else:
            # Other crypto asset: calculate USD value
            sym = f"{asset}USDT"
            c_price = get_symbol_price(sym, is_futures=False) or 0.0
            usd_val = total_qty * c_price
            if usd_val >= 0.5:  # Only show non-dust assets
                total_wallet_usd += usd_val
                crypto_holdings.append({
                    "asset": asset,
                    "symbol": sym,
                    "quantity": free_qty,
                    "price": c_price,
                    "usd_value": round(usd_val, 2),
                    "is_stable": asset in stablecoin_set
                })
                print(f"  🪙 {asset}: {free_qty:.4f} @ ${c_price:.4f} = ${usd_val:.2f} USD")
                
    print(f"  💰 SALDO TOTAL NETO EN CUENTA: ${total_wallet_usd:.2f} USD")
    print("="*60 + "\n")
    
    # Auto-adoption or clearance of active positions
    current_pos = state.get("position")
    significant_cryptos = [c for c in crypto_holdings if c["usd_value"] >= 5.0 and not c["is_stable"]]
    
    if significant_cryptos:
        primary = significant_cryptos[0]
        if not current_pos or current_pos.get("symbol") != primary["symbol"]:
            exact_entry, exact_cost, exact_qty = get_exact_real_entry_price(primary["symbol"])
            final_entry = exact_entry if exact_entry else primary["price"]
            final_cost = exact_cost if exact_cost else primary["usd_value"]
            final_qty = exact_qty if exact_qty else primary["quantity"]
            state["position"] = {
                "symbol": primary["symbol"],
                "quantity": final_qty,
                "entry_price": final_entry,
                "highest_price": final_entry,
                "cost_usd": final_cost,
                "side": "LONG",
                "phase": 1,
                "break_even": False,
                "entry_time_ms": int(time.time() * 1000)
            }
            price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
            state["status"] = f"🔵 En Vivo LONG ({primary['symbol']} @ {price_fmt(final_entry)})"
            print(f"🎯 [AUTO-ADOPCIÓN EXACTA] Posición en {primary['symbol']} adoptada con precio real Binance: {price_fmt(final_entry)} (Costo: ${final_cost} USD).")
    else:
        # If we thought we had a position but no non-stable crypto >= $4 USD exists in wallet
        if current_pos and current_pos.get("side") == "LONG":
            held_sym = current_pos.get("symbol", "").replace("USDT", "")
            is_still_held = any(c["asset"] == held_sym and c["usd_value"] >= 4.0 for c in crypto_holdings)
            if not is_still_held:
                print(f"🧹 [AUTO-LIMPIEZA] La posición {current_pos.get('symbol')} ya no existe en Binance Spot (vendida/convertida). Estado liberado a 'Buscando'.")
                state["position"] = None
                state["status"] = "🟦 Buscando Entrada A+"
                
    state["_cached_total_val"] = round(total_wallet_usd, 2)
    state["_cached_usdt_free"] = round(usdt_free, 4)
    state["_cached_bnb"] = bnb_free
    state["_cached_bnb_usd"] = round(bnb_usd, 2)
    state["current_balance_usd"] = round(total_wallet_usd, 2)
    state["net_pnl_usd"] = round(total_wallet_usd - state.get("initial_deposit_usdt", 17.13), 2)
    save_real_account_state(state)
    return state

def transfer_usdt(amount, to_futures=True):
    """
    Transfers USDT between Spot and Futures automatically.
    """
    timestamp = int(time.time() * 1000)
    params = {
        "type": "MAIN_UMFUTURE" if to_futures else "UMFUTURE_MAIN",
        "asset": "USDT",
        "amount": f"{amount:.2f}",
        "timestamp": timestamp
    }
    query = urlencode(params)
    sig = hmac.new(API_SECRET.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    try:
        res = requests.post(f"{BASE_URL}/sapi/v1/asset/transfer", headers={"X-MBX-APIKEY": API_KEY}, params={**params, "signature": sig}, proxies=get_smart_proxy(), timeout=10)
        print(f"🔄 Auto-Transfer {'to Futures' if to_futures else 'to Spot'}: {res.json()}")
        return res.json()
    except Exception as e:
        print(f"Transfer failed: {e}")
        return {"error": str(e)}

def execute_real_futures_market_short(symbol, usdt_amount):
    """
    Opens a SHORT position on Binance Futures.
    STEP 1: Execute MARKET SELL to open the SHORT.
    STEP 2: Place SL/TP orders AFTER the position exists (fixes reduceOnly rejection).
    """
    timestamp = int(time.time() * 1000)
    clean_usd = int(usdt_amount * 0.98 * 100) / 100.0
    headers = {"X-MBX-APIKEY": API_KEY}

    # 0. Ensure funds are in Futures wallet (Auto-transfer from Spot)
    try:
        f_balance = get_real_futures_usdt_balance()
        amount_needed = (clean_usd + 0.1) - f_balance
        if amount_needed > 1.0:
            transfer_usdt(amount_needed, to_futures=True)
    except Exception as e:
        print(f"Error checking futures balance before transfer: {e}")
        transfer_usdt(clean_usd + 0.1, to_futures=True) # Fallback

    # 1. Force Isolated Margin (Ignore if already Isolated)
    try:
        m_params = {"symbol": symbol, "marginType": "ISOLATED", "timestamp": timestamp}
        m_query = urlencode(m_params)
        m_sig = hmac.new(API_SECRET.encode("utf-8"), m_query.encode("utf-8"), hashlib.sha256).hexdigest()
        requests.post(f"{FAPI_URL}/fapi/v1/marginType", headers=headers, params={**m_params, "signature": m_sig}, proxies=get_smart_proxy(), timeout=5)
    except Exception:
        pass

    # 2. Fetch live price AND correct quantity precision from exchangeInfo
    try:
        price_res = requests.get(f"{FAPI_URL}/fapi/v1/ticker/price?symbol={symbol}", proxies=get_smart_proxy(), timeout=5).json()
        price = float(price_res.get("price", 1.0))
        
        # Get correct quantity precision for this symbol
        qty_precision = 3  # default
        try:
            exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=get_smart_proxy(), timeout=5).json()
            sym_info = next((s for s in exinfo['symbols'] if s['symbol'] == symbol), None)
            if sym_info:
                qty_precision = int(sym_info.get('quantityPrecision', 3))
        except:
            pass
        
        qty = clean_usd / price
        if qty_precision == 0:
            qty = max(int(qty), 1)
            # Ensure notional (qty * price) >= $5.0 minimum
            while qty * price < 5.0:
                qty += 1
            qty_str = str(qty)
        else:
            qty = round(qty, qty_precision)
            qty_str = f"{qty:.{qty_precision}f}"
        
        # Final notional check
        notional = qty * price
        if notional < 5.0:
            return {"error": f"Notional too small: {qty} x ${price:.4f} = ${notional:.2f} (min $5.0)"}
        
        # Risk Management: SL +1.0% (loss), TP -2.0% (win) for SHORT
        # Get price precision too
        price_precision = 4
        try:
            if sym_info:
                price_filter = next((f for f in sym_info['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
                if price_filter:
                    tick = price_filter.get('tickSize', '0.0001')
                    price_precision = max(0, len(tick.rstrip('0').split('.')[-1])) if '.' in tick else 0
        except:
            pass
        sl_price = round(price * 1.01, price_precision)
        tp_price = round(price * 0.98, price_precision)
    except Exception as e:
        return {"error": f"Failed to calculate price/qty: {e}"}

    # 3. STEP 1: Execute MARKET SELL entry order FIRST
    timestamp = int(time.time() * 1000)
    entry_params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
        "timestamp": timestamp
    }
    entry_query = urlencode(entry_params)
    entry_sig = hmac.new(API_SECRET.encode("utf-8"), entry_query.encode("utf-8"), hashlib.sha256).hexdigest()
    entry_params["signature"] = entry_sig
    
    try:
        entry_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=entry_params, proxies=get_smart_proxy(), timeout=10)
        entry_data = entry_res.json()
        if "orderId" not in entry_data:
            return {"error": f"Entry order failed: {entry_data}"}
    except Exception as e:
        return {"error": f"Entry order exception: {e}"}
    
    # 4. STEP 2: Place SL and TP orders AFTER position exists (fixes reduceOnly -2022 rejection)
    time.sleep(0.5)  # Brief pause to ensure position is registered
    
    for sl_tp_type, stop_px, order_type in [("SL", sl_price, "STOP_MARKET"), ("TP", tp_price, "TAKE_PROFIT_MARKET")]:
        try:
            ts = int(time.time() * 1000)
            p = {
                "symbol": symbol,
                "side": "BUY",
                "type": order_type,
                "stopPrice": str(stop_px),
                "closePosition": "true",
                "timestamp": ts
            }
            q = urlencode(p)
            s = hmac.new(API_SECRET.encode("utf-8"), q.encode("utf-8"), hashlib.sha256).hexdigest()
            p["signature"] = s
            sl_tp_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=p, proxies=get_smart_proxy(), timeout=10)
            print(f"  ✅ {sl_tp_type} order placed: {sl_tp_res.json().get('orderId', sl_tp_res.text)}")
        except Exception as e:
            print(f"  ⚠️ {sl_tp_type} order failed: {e}")
    
    # Return the entry order result with orderId for state tracking
    return entry_data

def execute_real_futures_market_close(symbol, quantity):
    """Close an active SHORT position by placing a BUY MARKET order."""
    timestamp = int(time.time() * 1000)
    
    qty_precision = 3  # default
    try:
        exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=get_smart_proxy(), timeout=5).json()
        sym_info = next((s for s in exinfo['symbols'] if s['symbol'] == symbol), None)
        if sym_info:
            qty_precision = int(sym_info.get('quantityPrecision', 3))
    except:
        pass
        
    if qty_precision == 0:
        qty_str = str(int(quantity))
    else:
        qty_str = f"{quantity:.{qty_precision}f}"

    params = {
        "symbol": symbol,
        "side": "BUY",  # We are closing a SHORT, so we BUY
        "type": "MARKET",
        "quantity": qty_str,
        "reduceOnly": "true",
        "timestamp": timestamp
    }
        
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        res_json = res.json()
        
        # Only transfer balance back to spot if the close order was successful
        if "orderId" in res_json:
            try:
                f_balance = get_real_futures_usdt_balance()
                if f_balance > 1.0:
                    transfer_usdt(f_balance - 0.1, to_futures=False)
            except Exception as te:
                print(f"Error transferring back to spot: {te}")
            
        return res_json
    except Exception as e:
        return {"error": str(e)}

def calculate_dynamic_proportional_trailing(highest_pnl_pct: float, atr_pct: float, holding_cycles: int = 0, current_pnl_pct: float = 0.0, custom_slack: float = None, symbol: str = None):
    """
    🎯 ESCALERA CUÁNTICA DINÁMICA BASADA EN ADN DEL ACTIVO (4 ARQUETIPOS):
    Adapta el Stop-Loss, tiempo y trailing floor específicamente según el perfil fenotípico:
    - 🐆 HYPER_VOLATILE_SPRINT (Memes / High-Beta: PEPE, DOGE, HEI, PENGU, BARD) -> SL -2.80%, Cosecha Rápida +1.50%
    - 🏛️ BLUE_CHIP_CORE (Institucional: BTC, ETH, SOL, BNB, BCH, LINK) -> SL -2.00%, Trend Ride
    - 🧩 SECTOR_ROTATION (L2 / DeFi / AI: ARB, OP, AAVE, UNI, FET) -> SL -2.00%, Paciencia 35m
    - 🎯 THIN_BOOK_MICRO (Micro-Caps: MUB, TUT, GPS, DEXE) -> SL -1.50%, Salida rápida 15m
    """
    try:
        import adaptive_asset_dna
        if symbol:
            archetype_dna = adaptive_asset_dna.get_asset_dna_archetype(symbol, atr_pct)
        else:
            archetype_dna = adaptive_asset_dna.ARCHETYPE_CONFIGS["SECTOR_ROTATION"]
        return adaptive_asset_dna.calculate_archetype_trailing(
            archetype_dna=archetype_dna,
            highest_pnl_pct=highest_pnl_pct,
            current_pnl_pct=current_pnl_pct,
            holding_minutes=holding_cycles,
            atr_pct=atr_pct
        )
    except Exception as e:
        # Fallback to Wide Slack Trailing & Rally Capture Architecture
        if highest_pnl_pct >= 4.00:
            sl_pct = round(highest_pnl_pct * 0.80, 4)
            phase = 6
            phase_label = f"👑 FASE 6 MEGA RALLY (Cima +{highest_pnl_pct:.2f}% | Retención 80% -> Piso +{sl_pct:.2f}%)"
        elif highest_pnl_pct >= 2.00:
            sl_pct = round(highest_pnl_pct * 0.75, 4)
            phase = 5
            phase_label = f"🚀 FASE 5 TENDENCIA FUERTE (Cima +{highest_pnl_pct:.2f}% | Retención 75% -> Piso +{sl_pct:.2f}%)"
        elif highest_pnl_pct >= 1.00:
            sl_pct = round(highest_pnl_pct * 0.70, 4)
            phase = 4
            phase_label = f"💎 FASE 4 EXPANSIÓN MEDIA (Cima +{highest_pnl_pct:.2f}% | Retención 70% -> Piso +{sl_pct:.2f}%)"
        elif highest_pnl_pct >= 0.44:
            sl_pct = max(0.20, round(highest_pnl_pct * 0.65, 4))
            phase = 3
            phase_label = f"🔒 FASE 3 SEGURO DE GANANCIA +0.20% NETO (Cima +{highest_pnl_pct:.2f}% | Retención 65% -> Piso +{sl_pct:.2f}%)"
        elif highest_pnl_pct >= 0.35:
            sl_pct = max(0.08, round(highest_pnl_pct * 0.30, 4))
            phase = 2
            phase_label = f"🛡️ FASE 2 BREAK-EVEN BLINDADO (+0.08% NETO | Cima +{highest_pnl_pct:.2f}% -> Piso +{sl_pct:.2f}%)"
        else:
            sl_pct = -0.50
            phase = 1
            phase_label = f"🛡️ FASE 1 RESPIRACIÓN Y ABSORCIÓN (Cima +{highest_pnl_pct:.2f}% | SL Defensivo -0.50%)"
                
        return sl_pct, phase, phase_label

def quick_position_heartbeat():
    """
    Sub-second micro-monitor for active real-money Spot position.
    Runs every 5-10s between main matrix cycles.
    Instantly updates highest_price, unlocks phases, and triggers emergency SL/TP.
    """
    try:
        import adaptive_asset_dna
        state = load_real_account_state()
        pos = state.get("position")
        if not pos or not pos.get("symbol"):
            return None
            
        sym = pos.get("symbol")
        qty = float(pos.get("quantity", 0))
        entry = float(pos.get("entry_price", 0))
        if qty <= 0 or entry <= 0:
            return None
            
        # Fast direct price ticker
        current_price = get_symbol_price(sym, is_futures=False)
        if not current_price or current_price <= 0:
            return None
            
        # 🚀 DETECTOR CUÁNTICO DE MECHAS: Consulta velas de 1m (Local + Nube) solo DESPUÉS de la entrada
        entry_time_ms = pos.get("entry_time_ms", 0)
        kline_high = get_recent_kline_high(sym, limit=5, start_time_ms=entry_time_ms)
        highest_price = max(pos.get("highest_price", entry), current_price, kline_high if kline_high > 0 else current_price)
        highest_pnl_pct = ((highest_price - entry) / entry) * 100.0
        current_pnl_pct = ((current_price - entry) / entry) * 100.0
        current_phase = pos.get("phase", 1)
        
        atr_15m_pct = pos.get("atr_pct_15m", 0.30)
        ma25_5m = pos.get("ma25_5m", 0.0)
        custom_slack = float(pos.get("optimal_trailing_slack_pct", 0.65))
        arch_dna = pos.get("archetype_dna", {}) or adaptive_asset_dna.get_asset_dna_archetype(sym, atr_15m_pct, current_price)
        
        # ⏱️ CÁLCULO EXACTO DE TIEMPO TRANSCURRIDO (Segundo a Segundo en Minutos Reales)
        import time as _t
        now_ms = _t.time() * 1000.0
        if entry_time_ms > 0:
            holding_minutes_hb = int((now_ms - entry_time_ms) / 60000.0)
        else:
            holding_minutes_hb = int(pos.get("holding_cycles", 0) * 2)
        pos["holding_cycles"] = holding_minutes_hb // 2
        
        # ═══════════════════════════════════════════════════════════════════════
        # 🎯 SISTEMA PROPORCIONAL DINÁMICO FRACTAL BASADO EN ADN DEL ACTIVO:
        # ═══════════════════════════════════════════════════════════════════════
        sl_pct, new_phase, phase_label = calculate_dynamic_proportional_trailing(
            highest_pnl_pct=highest_pnl_pct,
            atr_pct=atr_15m_pct,
            holding_cycles=holding_minutes_hb // 2,
            current_pnl_pct=current_pnl_pct,
            custom_slack=custom_slack,
            symbol=sym
        )
        pos["volatility_regime"] = phase_label
            
        # Update if changed
        if highest_price > pos.get("highest_price", entry) or new_phase > current_phase:
            pos["highest_price"] = highest_price
            pos["phase"] = new_phase
            state["position"] = pos
            save_real_account_state(state)
            
        # Check if Stop Loss or Trailing Stop triggered (STRICT INVIOLABLE FLOOR)
        should_exit = current_pnl_pct <= sl_pct
        exit_reason = f"🎯 Trailing Floor Activado ({current_pnl_pct:+.2f}% <= {sl_pct:+.2f}%)"
        
        # 🎯 SNIPER COSECHA GANANCIA TEMPRANA (+0.44% A +0.70%):
        # Si tocó >= +0.44% (Fase 3) y retrocede >= 0.18% o cae cerca del piso neto, cosechar inmediatamente
        wick_pullback_threshold = max(0.18, min(0.35, round(custom_slack * 0.40, 2)))
        if not should_exit and new_phase >= 3 and highest_pnl_pct >= 0.44:
            if (highest_pnl_pct - current_pnl_pct) >= wick_pullback_threshold or current_pnl_pct <= 0.15:
                should_exit = True
                exit_reason = f"🎯 SNIPER COSECHA GANANCIA (Pico +{highest_pnl_pct:.2f}% -> Venta Asegurada en {current_pnl_pct:+.2f}% tras retroceso de -{wick_pullback_threshold:.2f}%)"
            
        # ⏱️ LIBERACIÓN ESTRICTA POR TIEMPO Y ESTANCAMIENTO (Máximo 35m Sector / 25m Thin / 15m Meme)
        max_stag_mins = int(arch_dna.get("max_stagnation_minutes", 35))
        if not should_exit and new_phase == 1:
            is_stag, stag_msg = adaptive_asset_dna.check_archetype_stagnation_exit(
                archetype_dna=arch_dna,
                holding_minutes=holding_minutes_hb,
                pnl_pct=current_pnl_pct,
                phase=new_phase
            )
            if is_stag:
                should_exit = True
                exit_reason = stag_msg
            elif holding_minutes_hb >= max_stag_mins and abs(current_pnl_pct) <= 0.65:
                should_exit = True
                exit_reason = f"⏱️ LÍMITE DE TIEMPO ESTRICTO: {sym} lleva {holding_minutes_hb}m sin despegue (PnL {current_pnl_pct:+.2f}% | Límite={max_stag_mins}m). Liberando 100% USDT para rotar a nuevo Setup A+."
        
        # 🧱 MEJORA 4: Cancelación Preventiva — Solo si el libro de órdenes colapsa severamente
        # Requiere pérdida > -1.50% y Bids < 30% para evitar falsas salidas por ruido de micro-spread
        if not should_exit and holding_minutes_hb <= 2 and current_pnl_pct < -1.50:
            try:
                import orderbook_analyzer as _ob
                ob_check = _ob.fetch_orderbook_depth(sym, limit=20)
                bids_now = ob_check.get("bid_dominance_pct", 50.0)
                if bids_now < 30.0:
                    should_exit = True
                    exit_reason = f"⚡ CANCELACIÓN PREVENTIVA: Libro colapsó severamente (Bids={bids_now:.1f}% < 30%, PnL={current_pnl_pct:+.2f}%). Setup inválido."
            except Exception:
                pass
            
        if should_exit:
            print(f"\n🚨 [MICRO-HEARTBEAT 5S] Salida Inteligente ejecutada para {sym} @ ${current_price:.5f} ({exit_reason})")
            sell_res = execute_real_spot_market_sell(sym, qty)
            print(f"🔄 Venta Mercado Ejecutada: {sell_res}")
            
            # 📚 BUG FIX: Registrar win/loss correctamente + notificar learning engine
            pnl_usd = round((current_price - entry) * qty, 4)
            is_win_exit = current_pnl_pct > 0
            if is_win_exit:
                state["wins"] = state.get("wins", 0) + 1
                state["daily_wins"] = state.get("daily_wins", 0) + 1
            else:
                state["losses"] = state.get("losses", 0) + 1
                state["daily_losses"] = state.get("daily_losses", 0) + 1
            state["trades_count"] = state.get("trades_count", 0) + 1
            state["net_pnl_usd"] = round(state.get("net_pnl_usd", 0.0) + pnl_usd, 4)
            
            # 📖 Guardar en Learning Engine para memoria y aprendizaje de futuros trades
            try:
                import learning_engine
                trade_ctx = {
                    "score": pos.get("score", 80),
                    "rsi_15m": pos.get("rsi_15m", 50.0),
                    "atr_pct_15m": pos.get("atr_pct_15m", 0.45),
                    "vol_surge": pos.get("vol_surge", 1.0),
                    "vol_surge_1m": pos.get("vol_surge_1m", 1.0),
                    "fii_score": pos.get("fii_score", 60),
                    "obv_trend": pos.get("obv_trend", "ACCUMULATING"),
                    "macro_trend_4h": "NEUTRAL"
                }
                learning_engine.record_trade_outcome(
                    symbol=sym,
                    side="LONG",
                    entry_price=entry,
                    exit_price=current_price,
                    pnl_usd=pnl_usd,
                    result_type="WIN" if is_win_exit else "LOSS",
                    notes=f"Real Money Trade exited via {exit_reason} (Fase {new_phase}, PnL: {current_pnl_pct:+.2f}%)",
                    account_id="R-01",
                    group_name="CUENTA REAL",
                    context=trade_ctx
                )
            except Exception as le_err:
                print(f"⚠️ Learning Engine registro fallido: {le_err}")
            
            state["position"] = None
            state["status"] = f"{'🟢 WIN' if is_win_exit else '🔴 LOSS'} Cerrado ({sym} PnL: {current_pnl_pct:+.2f}% / ${pnl_usd:+.4f})"
            state["_last_closed_symbol"] = sym
            state["_last_closed_time"] = time.time()
            state["_last_exit_price"] = current_price
            save_real_account_state(state)
            try:
                diagnose_full_spot_wallet()
            except Exception:
                pass
            return "EXIT"
            
        return {
            "symbol": sym,
            "price": current_price,
            "pnl_pct": current_pnl_pct,
            "highest_pnl": highest_pnl_pct,
            "phase": new_phase
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

def trunc_1d(val):
    """Truncates a float to exactly 1 decimal place WITHOUT rounding."""
    if val is None:
        return 0.0
    import math
    return math.floor(float(val) * 10.0) / 10.0

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False, is_learned_signal=False, best_confidence=75, candidates_list=None):
    state = load_real_account_state()
    import math
    
    # Null guard on current_price
    if not current_price or current_price <= 0:
        current_price = 1.0
    
    # AUTOMATIC COMPOUND INTEREST ALLOCATION (SPOT ONLY - EXACTLY 1 POSITION AT A TIME)
    # Strictly truncated to 1 decimal place WITHOUT rounding, minus 0.1 USD buffer for Binance spot fees
    raw_usdt = state.get("_cached_usdt_free", state.get("current_balance_usd", 0.0))
    truncated_1d = trunc_1d(raw_usdt)
    usdt_free = max(0.0, trunc_1d(truncated_1d - 0.1))
    
    crypto_balances = []
    
    # Hydrate crypto_balances from local state
    if state.get("position"):
        pos = state["position"]
        qty = pos.get("quantity", pos.get("cost_usd", 10.0) / max(pos.get("entry_price", 1.0), 0.0001))
        if pos.get("side") == "LONG":
            crypto_balances = [{"asset": pos["symbol"].replace("USDT", ""), "free": qty}]
    
    # --- LEARNING ENGINE INTEGRATION ---
    market_bias = None
    try:
        import learning_engine
        market_bias = learning_engine.get_market_bias()
    except Exception:
        pass
    
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    # ========================================
    # CASE 1: We have an active LONG position
    # ========================================
    if crypto_balances:
        active_asset = crypto_balances[0]["asset"]
        active_qty = float(crypto_balances[0]["free"])
        active_symbol = f"{active_asset}USDT"
        
        import multi_timeframe_analyzer
        # AUTO-LIQUIDATION GUARD FOR UUSDT OR STABLECOIN POSITIONS
        if multi_timeframe_analyzer.is_stablecoin(active_symbol) or active_symbol == "UUSDT":
            print(f"🚨 DETECTADA POSICIÓN EN STABLECOIN / DÓLAR SINTÉTICO ({active_symbol}). Ejecutando Venta de Emergencia para restaurar saldo USDT...")
            sell_res = execute_real_spot_market_sell(active_symbol, active_qty)
            print(f"🔄 Venta de Emergencia {active_symbol}: {sell_res}")
            state["position"] = None
            state["status"] = "🟦 Buscando Entrada A+"
            save_real_account_state(state)
            return state
            
        # Fetch live price of the held asset
        active_current_price = get_symbol_price(active_symbol, is_futures=False)
        if not active_current_price:
            active_current_price = current_price  # Fallback
            
        est_val = active_qty * active_current_price
        entry = state["position"].get("entry_price", active_current_price)
        pnl_pct = ((active_current_price - entry) / entry) * 100.0 if entry > 0 else 0.0
        pnl_usd = (active_current_price - entry) * active_qty
        
        # Track Highest Price Reached for Dynamic Trailing Stop (incluyendo mechas de velas 1m para Local y Nube)
        kline_high = get_recent_kline_high(active_symbol, limit=5)
        highest_price = max(state["position"].get("highest_price", entry), active_current_price, kline_high)
        highest_pnl_pct = ((highest_price - entry) / entry) * 100.0 if entry > 0 else 0.0
        
        holding_cycles = state["position"].get("holding_cycles", 0) + 1
        
        atr_15m_pct = state["position"].get("atr_pct_15m", 0.30)
        ma25_5m = state["position"].get("ma25_5m", 0.0)
        
        import orderbook_analyzer
        
        # ═══════════════════════════════════════════════════════════════
        # 🎯 SISTEMA ULTRA-EFICIENTE DE 3 FASES ASIMÉTRICAS:
        # FASE 1: Antes de +0.55% -> SL -2.00% (Margen amplio para absorber volatilidad y permitir despegue).
        # FASE 2: +0.55% a +1.10% -> Piso = max(+0.18% NETO, Cima - holgura).
        # FASE 3: Superior a +1.10% -> Trailing Holgado ATR = CIMA - dynamic_trailing_distance.
        # ═══════════════════════════════════════════════════════════════
        # 🎯 SISTEMA PROPORCIONAL DINÁMICO CONTINUO BASADO EN CIMA ALCANZADA:
        # ═══════════════════════════════════════════════════════════════
        custom_slack = float(state["position"].get("optimal_trailing_slack_pct", 0.65))
        trailing_floor_pct, phase, phase_msg = calculate_dynamic_proportional_trailing(
            highest_pnl_pct=highest_pnl_pct,
            atr_pct=atr_15m_pct,
            holding_cycles=holding_cycles,
            current_pnl_pct=pnl_pct,
            custom_slack=custom_slack
        )

        # ESCUDO 1: BTC Flash Crash Circuit Breaker
        btc_price_now = get_symbol_price("BTCUSDT", is_futures=False)
        btc_crash_emergency = False
        if btc_price_now and active_symbol != "BTCUSDT":
            btc_prev = state.get("_btc_last_price", btc_price_now)
            state["_btc_last_price"] = btc_price_now
            btc_drop_pct = ((btc_price_now - btc_prev) / btc_prev) * 100.0 if btc_prev > 0 else 0.0
            if btc_drop_pct <= -1.5:
                btc_crash_emergency = True
                print(f"🚨 ESCUDO 1 (BTC Flash Crash): BTC cayó {btc_drop_pct:.2f}%. Freno de emergencia!")

        # ESCUDO 2: Guardia de Muro Inverso de Liquidez (Orderbook Wall Flip)
        ob_depth = orderbook_analyzer.fetch_orderbook_depth(active_symbol)
        ask_dominance = 100.0 - ob_depth.get("bid_dominance_pct", 50.0)
        orderbook_wall_emergency = False
        if ask_dominance >= 75.0:  # Raised to 75% to avoid false alarms
            orderbook_wall_emergency = True
            print(f"🧱 ESCUDO 2 (Muro Inverso): Vendedores dominan {ask_dominance:.1f}%!")

        # Emergency override: Only in Phase 1 (before any profit was reached)
        if (btc_crash_emergency or orderbook_wall_emergency) and phase == 1:
            trailing_floor_pct = max(-2.00, trailing_floor_pct)
            phase_msg = f"🛡️ ESCUDO DE EMERGENCIA: SL ajustado a {trailing_floor_pct:+.2f}%"

        # ⏱️ Liberación Estricta por Estancamiento y Tiempo Límite según ADN (35m Sector / 25m Thin / 15m Meme):
        stagnation_exit = False
        reason_str = ""
        import adaptive_asset_dna
        arch_dna_track = adaptive_asset_dna.get_asset_dna_archetype(active_symbol, atr_15m_pct)
        max_stag_mins = int(arch_dna_track.get("max_stagnation_minutes", 35))
        
        entry_ts_ms = state.get("position", {}).get("entry_time_ms", 0)
        import time as _t
        now_ts_ms = _t.time() * 1000.0
        real_holding_minutes = int((now_ts_ms - entry_ts_ms) / 60000.0) if entry_ts_ms > 0 else int(holding_cycles * 2)
        
        # 1. Liberación por Estancamiento Máximo según ADN (Fase 1 plana sin despegue):
        if real_holding_minutes >= max_stag_mins and phase == 1 and abs(pnl_pct) <= 0.65:
            stagnation_exit = True
            reason_str = f"⏱️ Liberación por Tiempo Límite ({real_holding_minutes}m >= {max_stag_mins}m en Fase 1 sin despegue, PnL={pnl_pct:+.2f}%)"
        # 2. 🔄 Rotación Alpha Dinámica — Tras 30 minutos si hay un alpha de oportunidad superior:
        elif real_holding_minutes >= 30 and phase == 1 and abs(pnl_pct) <= 0.40:
            if best_symbol and best_symbol != active_symbol and best_score >= 75 and not is_bearish:
                score_delta = best_score - 58  # Delta sobre el umbral mínimo de entrada
                if score_delta >= 16:
                    stagnation_exit = True
                    reason_str = f"🔄 Rotación Alpha Dinámica ({real_holding_minutes}m plano → {best_symbol} @ {best_score}pts, delta={score_delta}pts)"
        
        # 🧠 MEJORA 6: FII en Tiempo Real durante el Holding — Re-evalúa cada 5 ciclos
        # Si el dinero institucional salió (FII < 20) y tenemos pérdida severa (> -1.50%), salir
        if not stagnation_exit and phase == 1 and holding_cycles >= 10 and holding_cycles % 5 == 0 and pnl_pct < -1.50:
            try:
                import multi_timeframe_analyzer as _mtf_live
                mtf_live_data = _mtf_live.analyze_multi_timeframe_candles(active_symbol)
                fii_live = mtf_live_data.get("fii_score", 50)
                if fii_live < 20:
                    stagnation_exit = True
                    reason_str = f"🧠 FII COLAPSÓ EN TIEMPO REAL ({fii_live}/100 < 20): Capital institucional salió. Salida anticipada al SL."
                    print(f"⚠️ [FII LIVE] {active_symbol} FII={fii_live}/100. Capital institucional salió → salida preventiva.")
            except Exception:
                pass

        sl_target = entry * (1.0 + (trailing_floor_pct / 100.0))
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "highest_price": highest_price,
            "cost_usd": round(est_val, 2),
            "side": "LONG",
            "phase": phase,
            "holding_cycles": holding_cycles,
            "volatility_regime": phase_msg
        }
        price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ {price_fmt(active_current_price)})"
        
        # --- MONITOREO ACTIVO PRIORITARIO (CADA 2 MINUTOS) ---
        print("\n" + "="*65)
        print(f"📊 [SEGUIMIENTO DE POSICIÓN ACTIVA REAL - SPOT]")
        print(f"🪙 Moneda: {active_symbol} | Cantidad: {active_qty:,.2f} {active_asset} (Tiempo: {holding_cycles}m / 2880m)")
        print(f"💵 Entrada: {price_fmt(entry)} USD | Máximo Pico: {price_fmt(highest_price)} USD (+{highest_pnl_pct:.2f}%)")
        print(f"📈 PnL Flotante Actual: {pnl_pct:+.2f}% (${pnl_usd:+.4f} USD)")
        print(f"🧠 {phase_msg}")
        print(f"🛡️ Piso de Salida: {price_fmt(sl_target)} USD ({trailing_floor_pct:+.2f}%)")
        print(f"🏰 Escudos: BTC [{'🔴' if btc_crash_emergency else '🟢'}] | Orderbook [{'🔴' if orderbook_wall_emergency else '🟢'}]")
        print("="*65 + "\n")
        
        # Check for exit condition (PRICE-DRIVEN, NOT TIME-DRIVEN)
        if entry and entry > 0:
            should_exit = False
            # SNIPER AGOTAMIENTO DE MECHA EN CIMA (Asegura el 80% del pico en Fase >= 2)
            wick_pullback_threshold = max(0.28, min(0.38, round(custom_slack * 0.5, 2)))
            if phase >= 2 and highest_pnl_pct >= 0.70 and (highest_pnl_pct - pnl_pct) >= wick_pullback_threshold:
                should_exit = True
                reason_str = f"🎯 SNIPER MECHA CIMA (Pico +{highest_pnl_pct:.2f}% → Venta Inmediata en {pnl_pct:+.2f}% tras retroceso de -{wick_pullback_threshold:.2f}%)"
            elif pnl_pct <= trailing_floor_pct:
                should_exit = True
                if phase >= 2:
                    reason_str = f"Protección de Ganancia Fase {phase} (Pico +{highest_pnl_pct:.2f}% → Venta en {pnl_pct:+.2f}%)"
                else:
                    reason_str = f"Stop Loss Fase 1 ({pnl_pct:.2f}% tocó piso de {trailing_floor_pct:+.2f}%)"
            elif phase >= 2 and orderbook_wall_emergency:
                should_exit = True
                reason_str = f"⚡ Salida Relámpago por Agotamiento CVD (Fase {phase}, Pico +{highest_pnl_pct:.2f}% → Vendedores dominan {ask_dominance:.1f}%)"
            elif stagnation_exit:
                should_exit = True
                reason_str = f"Liberación por Estancamiento (2 Días en Fase 1, PnL={pnl_pct:+.2f}%)"
                
            if should_exit:
                print(f"🎯 ALERTA REAL: Salida LONG por {reason_str} en {active_symbol}. Vendiendo...")
                
                try:
                    res_json = execute_real_spot_market_sell(active_symbol, active_qty)
                    if "orderId" in res_json or res_json.get("status") == "FILLED":
                        pnl_usd = (active_current_price - entry) * active_qty
                        
                        # Update daily counters
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        if state.get("last_trading_day") != today_str:
                            state["daily_wins"] = 0
                            state["daily_losses"] = 0
                            state["last_trading_day"] = today_str
                        
                        if pnl_usd > 0:
                            state["wins"] = state.get("wins", 0) + 1
                            state["daily_wins"] = state.get("daily_wins", 0) + 1
                            res_type = "WIN"
                        else:
                            state["losses"] = state.get("losses", 0) + 1
                            state["daily_losses"] = state.get("daily_losses", 0) + 1
                            res_type = "LOSS"
                            
                        state["trades_count"] = state.get("trades_count", 0) + 1
                        save_real_account_state(state)
                        # Sync exact live balances from Binance API
                        try:
                            diagnose_full_spot_wallet()
                        except Exception:
                            pass
                            
                        try:
                            import learning_engine
                            trade_ctx = {
                                "score": state.get("position", {}).get("score", 80),
                                "rsi_15m": state.get("position", {}).get("rsi_15m", 50.0),
                                "atr_pct_15m": state.get("position", {}).get("atr_pct_15m", 0.45),
                                "vol_surge": state.get("position", {}).get("vol_surge", 1.0),
                                "vol_surge_1m": state.get("position", {}).get("vol_surge_1m", 1.0),
                                "fii_score": state.get("position", {}).get("fii_score", 60),
                                "obv_trend": state.get("position", {}).get("obv_trend", "ACCUMULATING"),
                                "macro_trend_4h": "NEUTRAL"
                            }
                            learning_engine.record_trade_outcome(
                                symbol=active_symbol, side="BUY", entry_price=entry, exit_price=active_current_price,
                                pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money Trade closed with {pnl_pct:.2f}%",
                                account_id="R-01", group_name="CUENTA REAL", context=trade_ctx
                            )
                        except Exception as le:
                            print(f"Learning engine error: {le}")
                        
                        state["position"] = None
                        state["status"] = "🟦 Buscando Entrada A+"
                        state["_last_closed_symbol"] = active_symbol
                        state["_last_closed_time"] = time.time()
                        state["_last_exit_price"] = active_current_price
                        print(f"✅ LONG cerrado exitosamente: {res_type} ({pnl_pct:+.2f}% | ${pnl_usd:+.2f})")
                    else:
                        print(f"⚠️ Spot SELL rejected: {res_json}")
                except Exception as e:
                    print(f"Error ejecutando venta real: {e}")
                    
    # ========================================
    # CASE 2: No active position - Look for SPOT LONG Entry (15-FINALIST CASCADE)
    # ========================================
    else:
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"
        
        # 🚫 Stablecoin & Non-Speculative Commodity Peg filter (USDT, USDC, PAXG, XAUT, etc.)
        stablecoins_blacklist = {
            "USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "RLUSD", "USD1",
            "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD",
            "PAXG", "XAUT", "XAUt", "GOLD"
        }
        
        # 🏆 WHITELIST PRIORITARIA v2: Bonus de score para símbolos con alto rendimiento histórico
        priority_whitelist = {
            "KITEUSDT", "KITE", "BNBUSDT", "BNB", "ARBUSDT", "ARB", "BCHUSDT", "BCH",
            "ONTUSDT", "ONT", "LDOUSDT", "LDO", "NOTUSDT", "NOT", "PROMUSDT", "PROM",
            "XPLUSDT", "XPLUS", "ATOMUSDT", "ATOM", "2ZUSDT", "2Z", "HOMEUSDT", "HOME"
        }
        
        # --- ENTRY DECISION LOGIC (SPOT ONLY) ---
        import strategy_engine
        dyn_t = strategy_engine.load_thresholds()
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 65)
        min_required_score = max(70, real_long_score)
        
        # Check learning engine bias before entering
        bias_ok = True
        if market_bias:
            bias_direction = market_bias.get("recommended_bias", "NEUTRAL")
            if not is_bearish and bias_direction == "STRONG_SHORT":
                bias_ok = False
                print(f"🧠 Learning Engine BLOCKED LONG: Market bias is STRONG_SHORT")
        
        if not bias_ok or is_bearish:
            print("🔒 [ESCUDO MERCADO] Mercado bajista o sesgo en corto. Preservando 100% USDT.")
            return
            
        # ═════════════════════════════════════════════════════════════════════════
        # 🧬 ANÁLISIS EN CASCADA DE ADN ACTIVO PARA LOS 15 FINALISTAS DEL MERCADO:
        # Evalúa en orden de calidad institucional hasta encontrar el ganador 100% A+
        # ═════════════════════════════════════════════════════════════════════════
        candidate_queue = []
        if best_symbol and best_symbol != "NONE":
            candidate_queue.append({
                "symbol": best_symbol,
                "score": best_score,
                "price": current_price,
                "is_ai_champion": is_learned_signal
            })
            
        if candidates_list:
            for c in candidates_list:
                csym = c.get("symbol")
                if csym and csym not in [q["symbol"] for q in candidate_queue]:
                    cscore = c.get("score", 50)
                    cprice = c.get("tech_data", {}).get("current_price", 0.0)
                    candidate_queue.append({
                        "symbol": csym,
                        "score": cscore,
                        "price": cprice,
                        "is_ai_champion": False
                    })
        
        # Limit to top 15 finalists
        candidate_queue = candidate_queue[:15]
        
        if not candidate_queue:
            return
            
        print(f"\n🔬 [SÚPER-CEREBRO 15 FINALISTAS] Iniciando escaneo secuencial de ADN Activo y Confluencia 5-TF en {len(candidate_queue)} activos...")
        
        executed_trade = False
        import adaptive_asset_dna
        import multi_timeframe_analyzer
        import orderbook_analyzer
        
        last_closed_sym = state.get("_last_closed_symbol")
        last_closed_time = state.get("_last_closed_time", 0)
        last_exit_price = state.get("_last_exit_price", 0.0)
        now_epoch = time.time()
        
        for cand_idx, cand_info in enumerate(candidate_queue, 1):
            cand_sym = cand_info["symbol"]
            cand_score = cand_info["score"]
            cand_price = cand_info["price"]
            is_ai_top = cand_info.get("is_ai_champion", False)
            sym_clean = cand_sym.replace("USDT", "")
            
            # 1. Skip Stablecoins
            if sym_clean in stablecoins_blacklist or cand_sym in stablecoins_blacklist:
                continue
                
            # 2. Get live price if missing
            if not cand_price or cand_price <= 0:
                cand_price = get_symbol_price(cand_sym)
                if not cand_price or cand_price <= 0:
                    continue
                    
            # 3. 🧬 ADN ADAPTATIVO & CLASIFICACIÓN FENOTÍPICA
            cand_archetype = adaptive_asset_dna.get_asset_dna_archetype(
                symbol=cand_sym,
                price=cand_price
            )
            
            # 4. Cooldown 4H Anti-Resaca (se permite cascadear si es cooldown)
            if cand_sym == last_closed_sym and (now_epoch - last_closed_time) < 14400:
                discount_from_exit_pct = ((last_exit_price - cand_price) / last_exit_price) * 100.0 if (last_exit_price > 0 and cand_price > 0) else 0.0
                time_since_last_exit = now_epoch - last_closed_time
                if not (is_ai_top and time_since_last_exit >= 300) and not (discount_from_exit_pct >= 1.50 and time_since_last_exit >= 180):
                    mins_passed = int(time_since_last_exit / 60)
                    print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] En Cooldown 4H ({mins_passed}m transcurridos). Pasando al siguiente finalista...")
                    continue  # Cooldown is temporal, cascading is OK
            
            # 5. Multi-Timeframe Institutional Analysis (1m, 2m, 5m, 15m, 1h)
            mtf_res = multi_timeframe_analyzer.analyze_multi_timeframe_candles(cand_sym)
            tf_align = mtf_res.get("timeframe_alignment", {})
            atr_15m = mtf_res.get("atr_pct_15m", 0.45)
            
            # Re-evaluate archetype with live 15M ATR
            arch_dna = adaptive_asset_dna.get_asset_dna_archetype(cand_sym, atr_15m, cand_price)
            print(f"🧬 [ADN ACTIVO #{cand_idx}/15] {cand_sym} ({cand_score} Pts) -> {arch_dna.get('label')} (ATR={atr_15m:.2f}%, SL={arch_dna.get('initial_sl_pct')}%, MaxT={arch_dna.get('max_stagnation_minutes')}m)")
            
            # 6. Veto Zombi / Mega-Cap lenta (ATR < 0.35%)
            if arch_dna.get("is_low_volatility_zombie", False):
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por ATR insuficiente ({atr_15m:.2f}% < 0.35% o Mega-Cap lenta).")
                continue
                
            tf_1m = tf_align.get("1m", "BEARISH")
            tf_2m = tf_align.get("2m", "BEARISH")
            tf_5m = tf_align.get("5m", "BEARISH")
            tf_15m = tf_align.get("15m", "BEARISH")
            tf_1h = tf_align.get("1h", "BEARISH")
            tf_10s = tf_align.get("10s", "BEARISH")
            tf_30s = tf_align.get("30s", "BEARISH")
            fii = mtf_res.get("fii_score", 0)
            
            # Macro Base Check
            is_macro_base = (
                tf_1h == "BULLISH" or 
                mtf_res.get("is_yellow_arrow_1h") or 
                mtf_res.get("rsi_1h", 50) <= 55.0 or 
                mtf_res.get("range_position_1h", 0.5) <= 0.50 or 
                mtf_res.get("is_vwap_floor_rebound") or
                mtf_res.get("is_bullish_divergence")
            )
            is_structural_15m_base = (
                tf_15m == "BULLISH" or 
                mtf_res.get("is_yellow_arrow_pivot") or 
                mtf_res.get("is_ma7_above_ma25_upward") or 
                mtf_res.get("is_cetus_rocket_pattern") or
                mtf_res.get("is_ground_zero_micro_ignition")
            )
            
            has_dual_sub_minute_ignition = bool(
                (tf_10s == "BULLISH" and tf_30s == "BULLISH") or
                (tf_10s == "BULLISH" and tf_1m == "BULLISH" and mtf_res.get("vol_surge_10s", 1.0) >= 1.2) or
                (fii >= 60 and tf_10s == "BULLISH")
            )
            
            has_floor_turnaround = bool(
                tf_1m == "BULLISH" or
                tf_2m == "BULLISH" or
                mtf_res.get("is_bullish_divergence") or
                mtf_res.get("is_yellow_arrow_pivot") or
                mtf_res.get("is_vwap_floor_rebound") or
                mtf_res.get("is_ema_golden_cross") or
                has_dual_sub_minute_ignition
            )
            
            is_active_falling_knife = bool(
                (tf_10s == "BEARISH" and tf_30s == "BEARISH" and tf_1m == "BEARISH") and
                not mtf_res.get("is_bullish_divergence") and
                not mtf_res.get("is_vwap_floor_rebound")
            )
            
            is_15m_cascade = mtf_res.get("is_15m_red_cascade", False)
            is_at_daily_ceiling = mtf_res.get("is_at_daily_resistance_ceiling", False)
            
            if is_at_daily_ceiling or is_15m_cascade or is_active_falling_knife:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Techo/Cascada/Cuchillo.")
                continue
                
            if mtf_res.get("obv_trend") == "DISTRIBUTING":
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Distribución Institucional (OBV=DISTRIBUTING).")
                continue
                
            # 🎯 VETO DE CONFLUENCIA FRACTAL DE SUELO (1M + 2M + 5M + 15M + 30M + 1H):
            # Prohibido entrar si el precio está en el centro o techo de 5M/15M/30M.
            # Exige que el activo esté en el PISO SIMULTÁNEO en todas las escalas temporales.
            range_pos_1m = mtf_res.get("range_position_1m", 0.50)
            range_pos_2m = mtf_res.get("range_position_2m", 0.50)
            range_pos_5m = mtf_res.get("range_position_5m", 0.50)
            range_pos_15m = mtf_res.get("range_position_15m", 0.50)
            range_pos_30m = mtf_res.get("range_position_30m", 0.50)
            range_pos_1h = mtf_res.get("range_position_1h", 0.50)
            is_confluent_floor = mtf_res.get("is_confluent_fractal_floor", False)
            vol_1m_now = mtf_res.get("vol_surge_1m", 1.0)
            vol_15m_now = mtf_res.get("vol_surge_15m", 1.0)
            
            is_deep_pullback_base = bool(range_pos_15m <= 0.45 and range_pos_5m <= 0.45 and range_pos_1m <= 0.45)
            if not is_confluent_floor and not is_deep_pullback_base and not (vol_1m_now >= 2.5 or vol_15m_now >= 2.0):
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Falta de Suelo Fractal Confluente:")
                print(f"     Canales: [1M: {range_pos_1m*100:.0f}% | 2M: {range_pos_2m*100:.0f}% | 5M: {range_pos_5m*100:.0f}% | 15M: {range_pos_15m*100:.0f}% | 30M: {range_pos_30m*100:.0f}% | 1H: {range_pos_1h*100:.0f}%]")
                continue
                
            if not has_floor_turnaround:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Falta de Giro de Suelo en 1M/2M.")
                continue
                
            is_spring = mtf_res.get("spring_coiling", {}).get("is_spring_compressed", False)
            is_wave2 = mtf_res.get("wave2_retest", {}).get("is_wave2_retest", False)
            if (mtf_res.get("rsi_2m", 50.0) > 54.0 or mtf_res.get("rsi_1m", 50.0) > 54.0) and not (is_spring or is_wave2):
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Entrada Tardía (RSI 2M={mtf_res.get('rsi_2m'):.1f} > 54.0).")
                continue
                
            # 7. Orderbook Depth & Micro-Surge Checks
            ob_info = orderbook_analyzer.fetch_orderbook_depth(cand_sym, limit=20)
            spread_now = ob_info.get("spread_pct", 0.0)
            bid_dom_now = ob_info.get("bid_dominance_pct", 50.0)
            
            max_allowed_spread = 0.30 if ob_info.get("bid_vol_usdt", 0.0) >= 35000.0 else 0.26
            if spread_now > max_allowed_spread:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Spread excesivo ({spread_now:.3f}% > {max_allowed_spread:.3f}%).")
                continue
                
            if bid_dom_now < 49.0:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Bids insuficientes ({bid_dom_now:.1f}% < 49.0%).")
                continue
                
            if ob_info.get("bid_vol_usdt", 0.0) > 0 and ob_info.get("bid_vol_usdt", 0.0) < 15000.0:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Muro Bids delgado (${ob_info.get('bid_vol_usdt', 0.0):,.0f} < $15k).")
                continue
                
            vol_1m_now = mtf_res.get("vol_surge_1m", 1.0)
            vol_2m_now = mtf_res.get("vol_surge_2m", 1.0)
            vol_15m_now = mtf_res.get("vol_surge_15m", 1.0)
            is_30s_burst = mtf_res.get("is_30s_micro_burst", False)
            vol_acc = mtf_res.get("vol_acceleration", 1.0)
            is_pre_pump = mtf_res.get("is_pre_pump_signal", False)
            tf_1m_up = mtf_res.get("tf_1m_up", False)
            is_1m_wick = mtf_res.get("is_1m_lower_wick_absorption", False)
            
            # 🚀 REGLA DE IGNICIÓN DE VOLUMEN INTELIGENTE (Equilibrio perfecto: protege contra estancamiento sin frenar setups A+):
            is_dead_volume = (vol_1m_now < 0.40 and vol_15m_now < 0.50 and fii < 65)
            has_active_ignition = (vol_1m_now >= 0.80 or vol_2m_now >= 0.90 or vol_15m_now >= 1.10 or vol_acc >= 1.30 or is_pre_pump or is_30s_burst or fii >= 65)
            has_trigger_candle = (tf_1m_up or is_1m_wick or mtf_res.get("is_ground_zero_micro_ignition", False))
            
            if is_dead_volume or not has_active_ignition:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Volumen Muerto/Sin Ignición (1M={vol_1m_now:.2f}x, 15M={vol_15m_now:.2f}x, FII={fii}). Exige compradores activos.")
                continue
                
            if not has_trigger_candle:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Descartado por Vela 1M Roja en caída sin mecha de absorción. Exige giro verde.")
                continue
                
            final_cand_score = max(cand_score, mtf_res.get("multi_tf_score", 50))
            if final_cand_score < min_required_score:
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] Score insuficiente ({final_cand_score} < {min_required_score}).")
                continue
                
            # ═══════════════════════════════════════════════════════════════════════
            # 🎯 VERIFICACIÓN ADX/CCI + ADN HISTÓRICO DEL TOKEN (Inteligencia Final):
            # ═══════════════════════════════════════════════════════════════════════
            is_cci_overbought = mtf_res.get("is_cci_overbought", False)
            is_ranging = mtf_res.get("is_ranging_market", False)
            is_strong_trend = mtf_res.get("is_strong_trend", False)
            is_bullish_adx = mtf_res.get("is_bullish_trend_adx", False)
            is_cci_floor = mtf_res.get("is_cci_deep_oversold", False)
            adx_val = mtf_res.get("adx_15m_value")
            cci_val = mtf_res.get("cci_15m_value")
            
            # Veto CCI Overbought: Si el CCI está por encima de +150, el activo ya subió demasiado
            if is_cci_overbought and not (vol_1m_now >= 2.5):
                print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] CCI Sobrecomprado ({cci_val:.0f} >= 150). Entrada prohibida en cima.")
                continue
            
            # 🧬 CONSULTA DE ADN HISTÓRICO DEL TOKEN (Aprendizaje de las Simulaciones):
            token_dna_label = ""
            try:
                import learning_engine
                token_profile = learning_engine.get_token_dna_profile(cand_sym)
                token_wr = token_profile.get("win_rate", 50.0)
                token_trades = token_profile.get("total_trades", 0)
                
                if token_trades >= 3 and token_wr < 30.0:
                    print(f"  ⛔ [#{cand_idx}/15 {cand_sym}] ADN Histórico TÓXICO: WR={token_wr:.0f}% en {token_trades} trades. Blacklist dinámica.")
                    continue
                elif token_trades >= 3 and token_wr >= 65.0:
                    token_dna_label = f" | 🌟 ADN Élite ({token_wr:.0f}% WR en {token_trades} ops)"
                elif token_trades >= 3:
                    token_dna_label = f" | 📊 ADN ({token_wr:.0f}% WR en {token_trades} ops)"
            except Exception:
                pass
            
            # ═════════════════════════════════════════════════════════════════════════
            # 💎 TARJETA EJECUTIVA CUÁNTICA UNIFICADA (DICTAMEN IA + EJECUCIÓN SPOT)
            # ═════════════════════════════════════════════════════════════════════════
            trend_label = "📈 TENDENCIA FUERTE" if is_bullish_adx else ("📊 RANGO" if is_ranging else "📈 NEUTRAL")
            cci_label = f"CCI={cci_val:.0f}" if cci_val is not None else "CCI=N/A"
            adx_label = f"ADX={adx_val:.0f}" if adx_val is not None else "ADX=N/A"
            
            print(f"\n💎 ═══════════════════════════════════════════════════════════════════════════════════")
            print(f"🚀 [DICTAMEN & EJECUCIÓN CUÁNTICA SPOT: #{cand_idx}/15 -> {cand_sym}]")
            print(f"═══════════════════════════════════════════════════════════════════════════════════════")
            print(f"🧬 Arquetipo ADN: {cand_archetype.get('label')} | SL Inicial: -0.50% | Cosecha Fase 2: +0.44%{token_dna_label}")
            print(f"📊 Score MTF: {final_cand_score}/100 | FII Suelo: {fii}/100 | ATR: {atr_15m:.2f}% | Spread: {ob_info.get('spread_pct'):.3f}%")
            print(f"🌌 Canales Fractales: [1M: {range_pos_1m*100:.0f}% | 2M: {range_pos_2m*100:.0f}% | 5M: {range_pos_5m*100:.0f}% | 15M: {range_pos_15m*100:.0f}% | 30M: {range_pos_30m*100:.0f}% | 1H: {range_pos_1h*100:.0f}%]")
            print(f"🌊 Muro Comprador: ${ob_info.get('bid_vol_usdt', 0):,.0f} USDT (Bids={ob_info.get('bid_dominance_pct'):.1f}%) | OBV={mtf_res.get('obv_trend')}")
            print(f"📈 Tendencia: {trend_label} ({adx_label}) | {cci_label} | {'🟢 CCI Suelo' if is_cci_floor else '⚪ CCI Normal'}")
            print(f"═══════════════════════════════════════════════════════════════════════════════════════\n")
            
            # Pre-flight check live balance
            try:
                live_diag = diagnose_full_spot_wallet()
                live_usdt = live_diag.get("_cached_usdt_free", 0.0)
                if live_usdt < 5.1:
                    print(f"⚠️ [PRE-FLIGHT] Solo hay ${live_usdt:.2f} USDT libres en Binance Spot. Compra cancelada.")
                    return
                usdt_free = live_usdt
            except Exception:
                pass
                
            print(f"🚀 Ejecutando SPOT BUY en {cand_sym} con ${usdt_free:.2f} USDT (100% Capital)...")
            buy_res = execute_real_spot_market_buy(cand_sym, usdt_free)
            if isinstance(buy_res, dict) and "orderId" in buy_res:
                time.sleep(0.5)
                exact_entry, exact_cost, exact_qty = get_exact_real_entry_price(cand_sym)
                qty = exact_qty if exact_qty else float(buy_res.get("executedQty", 0))
                cum_quote = exact_cost if exact_cost else float(buy_res.get("cummulativeQuoteQty", 0))
                if exact_entry:
                    actual_entry_price = exact_entry
                    actual_cost = exact_cost
                elif qty > 0 and cum_quote > 0:
                    actual_entry_price = round(cum_quote / qty, 6)
                    actual_cost = round(cum_quote, 2)
                else:
                    actual_entry_price = cand_price
                    actual_cost = round(usdt_free, 2)
                if qty == 0:
                    qty = round(usdt_free / cand_price, 5)
                    
                arch_profile = adaptive_asset_dna.get_asset_dna_archetype(
                    symbol=cand_sym,
                    atr_15m_pct=atr_15m,
                    price=actual_entry_price
                )
                state["position"] = {
                    "symbol": cand_sym,
                    "entry_price": actual_entry_price,
                    "cost_usd": actual_cost,
                    "side": "LONG",
                    "quantity": qty,
                    "break_even": False,
                    "highest_price": actual_entry_price,
                    "phase": 1,
                    "archetype": arch_profile.get("archetype", "SECTOR_ROTATION"),
                    "archetype_label": arch_profile.get("label", "General"),
                    "initial_sl_pct": arch_profile.get("initial_sl_pct", -0.50),
                    "max_stagnation_minutes": arch_profile.get("max_stagnation_minutes", 60),
                    "vol_surge": mtf_res.get("vol_surge_2m", 1.0),
                    "vol_surge_1m": mtf_res.get("vol_surge_1m", 1.0),
                    "score": final_cand_score,
                    "rsi_15m": mtf_res.get("rsi_15m", 50.0),
                    "fii_score": fii,
                    "obv_trend": mtf_res.get("obv_trend", "ACCUMULATING"),
                    "entry_time_ms": int(time.time() * 1000),
                    "atr_pct_15m": atr_15m,
                    "ma25_5m": mtf_res.get("ma25_5m", cand_price),
                    "dna_tier": mtf_res.get("dna_profile", {}).get("dna_tier", "HIGH_BETA_RUNNER"),
                    "optimal_trailing_slack_pct": mtf_res.get("dna_profile", {}).get("optimal_trailing_slack_pct", 0.45),
                    "target_resistance_price": mtf_res.get("predictive_dna", {}).get("medium_term_horizon", {}).get("target_resistance_price", actual_entry_price * 1.03),
                    "pump_probability_pct": mtf_res.get("predictive_dna", {}).get("pump_probability_pct", 50)
                }
                state["status"] = f"🔵 En Vivo LONG ({cand_sym} @ ${actual_entry_price:.4f})"
                state["_cached_usdt_free"] = 0.0
                save_real_account_state(state)
                print(f"✅ SPOT LONG ejecutado exitosamente: {cand_sym} ({qty} @ ${actual_entry_price:.4f} = ${actual_cost} USD)")
                try:
                    import asset_dna_predictive_engine as _adna
                    _adna.register_trade_today(cand_sym)
                except Exception:
                    pass
                executed_trade = True
                break
                
        if not executed_trade:
            print(f"🔒 [CASCADE EVALUATION 15 FINALISTAS] Se evaluaron los {len(candidate_queue)} finalistas con ADN Activo y 5-TF. Ninguno superó el 100% de los filtros en este ciclo. 100% USDT protegido.")

    state["current_balance_usd"] = round(state.get("current_balance_usd", 20.07), 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - state.get("initial_deposit_usdt", 17.13), 2)
    state["last_trade_time"] = now_str
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
