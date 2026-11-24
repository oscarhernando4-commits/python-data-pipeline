
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
# MEGA-POOL FIXIE DINÁMICO DE 110 PROXIES HTTP (HASTA 55,000 REQ/MES)
# Proxies 11-110 (100 proxies): NUEVAS y activas HOY con 50,000 peticiones limpias (500 c/u).
# Proxies 1-10 (10 proxies): Se integran automáticamente el 2 de Septiembre (+5,000 peticiones).
# ============================================================

# POOL ACTIVO DE 100 PROXIES FIXIE (50,000 PETICIONES/MES)
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


# 🚫 BLACKLIST ABSOLUTO (auditoría forense 299 trades)
_API_BLACKLISTED = {
    "AEROUSDT", "DASHUSDT", "ICPUSDT", "APTUSDT", "MORPHOUSDT",
    "UNIUSDT", "AAVEUSDT", "DOTUSDT", "SUIUSDT", "FILUSDT",
    "OPUSDT", "LINKUSDT", "NEARUSDT", "CAKEUSDT", "PEPEUSDT"
}

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

def get_proxy_with_index():
    """Return (proxy_index, proxies_dict) using round-robin pool excluding exhausted accounts."""
    state = _load_proxy_state()
    idx = state.get("current_index", 9) % len(FIXIE_POOL)

    exhausted = state.get("exhausted", {})
    current_month = datetime.now().strftime("%Y-%m")
    last_exhaust_month = state.get("last_exhaust_month", "")
    if current_month != last_exhaust_month and exhausted:
        print(f"🔄 [FIXIE AUTO-RENOVACIÓN] Nuevo mes detectado ({current_month}). Reactivando las {len(exhausted)} cuentas Fixie pausadas.")
        exhausted = {}
        state["exhausted"] = {}
        state["last_exhaust_month"] = current_month
        _save_proxy_state(state)

    exhausted_indices = set(exhausted.get("indices", []))
    attempts = 0
    while idx in exhausted_indices and attempts < len(FIXIE_POOL):
        idx = (idx + 1) % len(FIXIE_POOL)
        attempts += 1

    if attempts >= len(FIXIE_POOL):
        print("⚠️ [FIXIE] TODAS las cuentas agotadas. Forzando reset de emergencia...")
        exhausted_indices = set()
        state["exhausted"] = {}
        idx = 9

    url = FIXIE_POOL[idx]
    state["current_index"] = (idx + 1) % len(FIXIE_POOL)
    usage = state.setdefault("usage", {})
    account_name = FIXIE_ACCOUNTS[idx]
    usage[account_name] = usage.get(account_name, 0) + 1
    state["last_used"] = account_name
    state["last_used_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _save_proxy_state(state)
    return idx, {"http": url, "https": url}


def get_proxy():
    """Round-Robin equitativo: rota secuencialmente entre cuentas Fixie activas con auto-renovación mensual."""
    _, proxies = get_proxy_with_index()
    return proxies


def _request_with_fixie_retry(method, url, headers=None, params=None, timeout=10, max_proxy_tries=4):
    """Execute HTTP request rotating across up to max_proxy_tries Fixie accounts on 402/407 or proxy failure."""
    if get_execution_mode() == "local":
        return requests.request(method, url, headers=headers, params=params, proxies=None, timeout=timeout)

    last_exc = None
    last_res = None
    for attempt in range(max_proxy_tries):
        idx, proxies = get_proxy_with_index()
        try:
            res = requests.request(method, url, headers=headers, params=params, proxies=proxies, timeout=timeout)
            last_res = res
            if res.status_code in (402, 407):
                mark_fixie_exhausted(idx)
                continue
            return res
        except Exception as exc:
            last_exc = exc
            err_s = str(exc).lower()
            if "402" in err_s or "407" in err_s or "proxy" in err_s:
                if "402" in err_s or "407" in err_s:
                    mark_fixie_exhausted(idx)
            continue

    if last_res is not None:
        return last_res
    # Last resort direct attempt if every Fixie try raised
    try:
        return requests.request(method, url, headers=headers, params=params, proxies=None, timeout=timeout)
    except Exception:
        if last_exc is not None:
            raise last_exc
        raise

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

# Flag para prevenir múltiples trades en el mismo ciclo de pipeline
# Se resetea al inicio de cada ciclo en cloud_continuous_loop.py
_trade_executed_this_cycle = False

# ============================================================
# STATE MANAGEMENT (Atomic writes to prevent corruption)
# ============================================================

def check_and_apply_utc_daily_reset(state):
    """
    Reinicia rigurosamente todos los acumuladores diarios a las 00:00:00 UTC.
    Garantiza que la meta diaria del 1.0%, el contador de operaciones y el PnL
    del día comiencen en CERO ($0.0000 USD, 0W/0L) en cada nuevo día UTC.
    """
    if not isinstance(state, dict):
        return False

    from datetime import datetime, timezone
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last_reset = state.get("last_daily_reset_date", "")
    pnl_date = state.get("_daily_pnl_date", "")

    # Si la fecha UTC actual no coincide con la fecha de reset o la fecha de PnL
    if last_reset != today_utc or pnl_date != today_utc:
        prev_w = state.get("daily_wins", 0)
        prev_l = state.get("daily_losses", 0)
        prev_pnl = state.get("_daily_pnl_usd", 0.0)

        state["daily_wins"] = 0
        state["daily_losses"] = 0
        state["_consecutive_losses"] = 0
        state["_daily_pnl_usd"] = 0.0
        state["_daily_pnl_date"] = today_utc
        state["last_daily_reset_date"] = today_utc
        state["last_trading_day"] = today_utc
        if not state.get("position"):
            state["status"] = "🟦 Buscando Entrada A+ (Modo Francotirador)"

        print(f"🔄 [REINICIO UTC 00:00] Nuevo día UTC ({today_utc}) detectado.", flush=True)
        print(f"   Contadores reiniciados a CERO: {prev_w}W/{prev_l}L | PnL previo: ${prev_pnl:+.4f} USD → $0.0000 USD.", flush=True)
        print(f"   🎯 Búsqueda de Meta Diaria 1.0% reactivada en Modo Francotirador.", flush=True)

        try:
            save_real_account_state(state)
        except Exception:
            pass
        return True
    return False

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
                state.setdefault("status", "🟦 Buscando Entrada A+ (Modo Francotirador)")
                state.setdefault("_daily_pnl_usd", 0.0)

                # ✅ RESET DIARIO AUTOMÁTICO A MEDIANOCHE UTC (00:00 UTC)
                check_and_apply_utc_daily_reset(state)

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
    api_k = get_api_key()
    api_s = get_api_secret()
    if not api_k or not api_s:
        return None
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}

    url = f"{BASE_URL}/api/v3/account"
    try:
        res = _request_with_fixie_retry("GET", url, headers=headers, params=params, timeout=8)
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

_FUTURES_CAPABLE_CACHE = {"ts": 0.0, "enabled": False}

def get_real_futures_balances():
    api_k = get_api_key()
    api_s = get_api_secret()
    if not api_k or not api_s:
        return None
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}

    url = f"{FAPI_URL}/fapi/v2/account"
    try:
        res = _request_with_fixie_retry("GET", url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("assets", [])
        return None
    except Exception:
        return None

def is_futures_trading_enabled(force_refresh: bool = False) -> bool:
    """Probe whether Binance USD-M Futures API is enabled on this API key (cached 15 min)."""
    global _FUTURES_CAPABLE_CACHE
    now = time.time()
    if not force_refresh and (now - _FUTURES_CAPABLE_CACHE.get("ts", 0.0)) < 900.0:
        return bool(_FUTURES_CAPABLE_CACHE.get("enabled", False))
    if not get_api_key() or not get_api_secret():
        _FUTURES_CAPABLE_CACHE = {"ts": now, "enabled": False}
        return False
    bals = get_real_futures_balances()
    enabled = isinstance(bals, list)
    _FUTURES_CAPABLE_CACHE = {"ts": now, "enabled": enabled}
    return enabled

def get_real_futures_positions():
    api_k = get_api_key()
    api_s = get_api_secret()
    if not api_k or not api_s:
        return []
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}

    url = f"{FAPI_URL}/fapi/v2/positionRisk"
    try:
        res = _request_with_fixie_retry("GET", url, headers=headers, params=params, timeout=10)
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
                        # FIX 1.3b: Incluir la vela del minuto de entrada (k[0] es inicio de vela, +60s cubre la vela completa)
                        filtered = [k for k in k_data if int(k[0]) + 60000 > int(start_time_ms)]
                        if filtered:
                            return max([float(k[2]) for k in filtered])
                        return 0.0
                    return max([float(k[2]) for k in k_data])
        except Exception:
            continue
            
    return 0.0

def get_klines(symbol: str, interval: str = "5m", limit: int = 3) -> list:
    """
    Fetches raw OHLCV kline data from Binance public mirrors.
    Returns list of klines: [open_time, open, high, low, close, volume, ...]
    Used by the BTC Pre-Entry Guard and Circuit Breaker.
    """
    mirrors = [
        "https://data-api.binance.vision/api/v3/klines",
        "https://api1.binance.com/api/v3/klines",
        "https://api2.binance.com/api/v3/klines",
        "https://api.binance.com/api/v3/klines",
    ]
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    for url in mirrors:
        try:
            res = requests.get(url, params=params, timeout=4)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            continue
    return []

def get_realtime_order_flow_momentum(symbol: str) -> dict:
    """
    ⚡ DETECTOR DE FLUJO DE ÓRDENES Y TAPE READING EN TIEMPO REAL:
    Monitorea las compras y ventas agresivas de mercado (Recent Trades Taker Flow)
    y la profundidad del libro (Order Book Imbalance) para cosechar ganancias en la cima:
    - taker_buy_pct: % de compras de mercado agresivas vs ventas
    - bid_dominance_pct: % de volumen en Bids frente a Asks
    - is_exhaustion_or_dump: Señal de que los compradores se agotaron y domina la venta
    Usa mirrors públicos directos (0 consumo de proxy Fixie).
    """
    mirrors = [
        "https://data-api.binance.vision/api/v3",
        "https://api1.binance.com/api/v3",
        "https://api2.binance.com/api/v3",
        "https://api3.binance.com/api/v3",
        "https://api.binance.com/api/v3"
    ]
    for base_url in mirrors:
        try:
            # 1. Consulta últimos 25 trades agresivos
            t_res = requests.get(f"{base_url}/trades?symbol={symbol}&limit=25", timeout=2.5)
            if t_res.status_code != 200:
                continue
            trades = t_res.json()
            if not isinstance(trades, list) or not trades:
                continue

            buy_vol = sum(float(t.get('price', 0)) * float(t.get('qty', 0)) for t in trades if not t.get('isBuyerMaker', False))
            sell_vol = sum(float(t.get('price', 0)) * float(t.get('qty', 0)) for t in trades if t.get('isBuyerMaker', False))
            tot_vol = buy_vol + sell_vol
            taker_buy_pct = (buy_vol / tot_vol * 100.0) if tot_vol > 0 else 50.0

            # 2. Consulta profundidad Top 10 Bids vs Asks
            d_res = requests.get(f"{base_url}/depth?symbol={symbol}&limit=10", timeout=2.5)
            depth = d_res.json() if d_res.status_code == 200 else {}
            bids = depth.get('bids', [])
            asks = depth.get('asks', [])

            bid_vol = sum(float(b[0]) * float(b[1]) for b in bids)
            ask_vol = sum(float(a[0]) * float(a[1]) for a in asks)
            tot_depth = bid_vol + ask_vol
            bid_dom_pct = (bid_vol / tot_depth * 100.0) if tot_depth > 0 else 50.0

            # FIX 2.4: Agotamiento calibrado a pánico real alcanzable:
            # Ventas agresivas taker (buy < 35%) Y (soporte débil bids < 40% O pánico extremo taker buy < 20%)
            is_exhaustion = bool(taker_buy_pct < 35.0 and (bid_dom_pct < 40.0 or taker_buy_pct < 20.0))

            return {
                "symbol": symbol,
                "taker_buy_pct": round(taker_buy_pct, 1),
                "taker_sell_pct": round(100.0 - taker_buy_pct, 1),
                "bid_dominance_pct": round(bid_dom_pct, 1),
                "ask_dominance_pct": round(100.0 - bid_dom_pct, 1),
                "is_exhaustion_or_dump": is_exhaustion
            }
        except Exception:
            continue

    return {
        "symbol": symbol,
        "taker_buy_pct": 50.0,
        "taker_sell_pct": 50.0,
        "bid_dominance_pct": 50.0,
        "ask_dominance_pct": 50.0,
        "is_exhaustion_or_dump": False
    }

# ============================================================
# ORDER EXECUTION (Uses Fixie proxy - counted towards quota)
# ============================================================

def execute_real_spot_market_buy(symbol, usdt_amount):
    """
    Executes a SPOT MARKET BUY using quoteOrderQty (100% free USDT).
    Rotates across Fixie proxies on failure and uses 2-decimal precision cleanly when needed.
    """
    import math
    timestamp = int(time.time() * 1000)
    state = load_real_account_state()

    cached_usdt = state.get("_cached_usdt_free", 0.0)
    if cached_usdt > 0:
        usdt_amount = min(usdt_amount, cached_usdt)

    # Preserve up to $5.10+ cleanly using 2-decimal floor (allows $5.25 -> $5.25 instead of dropping $0.05)
    clean_usd = math.floor(float(usdt_amount) * 100.0) / 100.0
    if clean_usd < 5.10:
        return {"error": f"MIN_NOTIONAL not met (${clean_usd:.2f} < $5.10)"}

    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{clean_usd:.2f}",
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
        res = _request_with_fixie_retry("POST", url, headers=headers, params=params, timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE OPENED] Sincronizando balance real desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after buy: {se}")
        return res_json
    except Exception as e:
        return {"error": str(e)}

def execute_real_spot_market_sell(symbol, quantity=None):
    """
    Executes a SPOT MARKET SELL.
    - Always clamps to live available free balance from Binance to avoid -2010 insufficient balance errors.
    - Rotates across healthy Fixie proxies on failure.
    """
    import math
    asset = symbol.replace("USDT", "")

    live_free = 0.0
    balances = get_real_balances()
    if balances:
        for b in balances:
            if b.get("asset") == asset:
                live_free = float(b.get("free", 0))
                break

    if live_free <= 0:
        return {"error": f"No available balance to sell for {symbol}"}

    if quantity is None or quantity > live_free:
        quantity = live_free

    try:
        ex_info = requests.get(f"{BASE_URL}/api/v3/exchangeInfo?symbol={symbol}", timeout=5).json()
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
    api_k = get_api_key()
    api_s = get_api_secret()
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}

    url = f"{BASE_URL}/api/v3/order"
    try:
        res = _request_with_fixie_retry("POST", url, headers=headers, params=params, timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE CLOSED] Sincronizando balance real en vivo desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after sell: {se}")
        return res_json
    except Exception as e:
        return {"error": str(e)}

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
            if bnb_usd < 0.08:
                print(f"  ⚠️ [ALERTA ESCUDO BNB] Balance de BNB bajo (~${bnb_usd:.2f} USD). Recomendable recargar $1-$2 USD en BNB para no perder el descuento del 25% en comisiones.", flush=True)
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
        # Check open Futures SHORT if enabled before clearing
        if current_pos and current_pos.get("side") == "SHORT":
            try:
                f_pos_list = get_real_futures_positions() if is_futures_trading_enabled() else []
                still_short = next((p for p in f_pos_list if p.get("symbol") == current_pos.get("symbol") and float(p.get("positionAmt", 0)) < 0), None)
                if not still_short and is_futures_trading_enabled():
                    print(f"🧹 [AUTO-LIMPIEZA FUTUROS] SHORT en {current_pos.get('symbol')} ya cerrado en Binance Futures. Estado liberado.")
                    state["position"] = None
                    state["status"] = "🟦 Buscando Entrada A+"
            except Exception:
                pass
        # If we thought we had a LONG position but no non-stable crypto >= $4 USD exists in wallet
        elif current_pos and current_pos.get("side") == "LONG":
            held_sym = current_pos.get("symbol", "").replace("USDT", "")
            is_still_held = any(c["asset"] == held_sym and c["usd_value"] >= 4.0 for c in crypto_holdings)
            if not is_still_held:
                print(f"🧹 [AUTO-LIMPIEZA] La posición {current_pos.get('symbol')} ya no existe en Binance Spot (vendida/convertida). Estado liberado a 'Buscando'.")
                state["position"] = None
                state["status"] = "🟦 Buscando Entrada A+"

    # Include Futures wallet balance when enabled
    futures_free_usd = 0.0
    try:
        if is_futures_trading_enabled():
            f_assets = get_real_futures_balances() or []
            for fa in f_assets:
                if fa.get("asset") in ("USDT", "USDC"):
                    wb = float(fa.get("walletBalance", 0.0)) + float(fa.get("crossUnPnl", 0.0))
                    futures_free_usd += float(fa.get("availableBalance", 0.0))
                    total_wallet_usd += wb
    except Exception:
        pass

    state["_cached_total_val"] = round(total_wallet_usd, 2)
    state["_cached_usdt_free"] = round(usdt_free, 4)
    state["_cached_futures_usdt_free"] = round(futures_free_usd, 4)
    state["_futures_enabled"] = is_futures_trading_enabled()
    state["_cached_bnb"] = bnb_free
    state["_cached_bnb_usd"] = round(bnb_usd, 2)
    state["current_balance_usd"] = round(total_wallet_usd, 2)
    state["net_pnl_usd"] = round(total_wallet_usd - state.get("initial_deposit_usdt", 17.13), 2)
    save_real_account_state(state)
    return state

def transfer_usdt(amount, to_futures=True):
    """Transfers USDT between Spot and Futures automatically using Fixie rotation."""
    api_k = get_api_key()
    api_s = get_api_secret()
    timestamp = int(time.time() * 1000)
    params = {
        "type": "MAIN_UMFUTURE" if to_futures else "UMFUTURE_MAIN",
        "asset": "USDT",
        "amount": f"{amount:.2f}",
        "timestamp": timestamp
    }
    query = urlencode(params)
    sig = hmac.new(api_s.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    try:
        res = _request_with_fixie_retry("POST", f"{BASE_URL}/sapi/v1/asset/transfer", headers={"X-MBX-APIKEY": api_k}, params={**params, "signature": sig}, timeout=10)
        print(f"🔄 Auto-Transfer {'to Futures' if to_futures else 'to Spot'}: {res.json()}")
        return res.json()
    except Exception as e:
        print(f"Transfer failed: {e}")
        return {"error": str(e)}


def _futures_signed_request(method, endpoint, params):
    api_k = get_api_key()
    api_s = get_api_secret()
    ts = int(time.time() * 1000)
    req_params = {**params, "timestamp": ts}
    q = urlencode(req_params)
    req_params["signature"] = hmac.new(api_s.encode("utf-8"), q.encode("utf-8"), hashlib.sha256).hexdigest()
    return _request_with_fixie_retry(method, f"{FAPI_URL}{endpoint}", headers={"X-MBX-APIKEY": api_k}, params=req_params, timeout=10)


def execute_real_futures_market_short(symbol, usdt_amount, leverage=2, sl_pct=-1.8, tp_pct=3.2):
    """Open an isolated Futures SHORT position with ATR-scaled exchange safety SL/TP."""
    clean_collateral = int(float(usdt_amount) * 0.98 * 100) / 100.0
    lev = max(1, min(3, int(leverage or 2)))

    # 0. Ensure collateral is in Futures wallet (Auto-transfer from Spot)
    try:
        f_balance = get_real_futures_usdt_balance()
        amount_needed = (clean_collateral + 0.15) - f_balance
        if amount_needed > 0.25:
            transfer_usdt(amount_needed, to_futures=True)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error checking futures balance before transfer: {e}")
        transfer_usdt(clean_collateral + 0.15, to_futures=True)

    # 1. Force Isolated Margin & Leverage
    try:
        _futures_signed_request("POST", "/fapi/v1/marginType", {"symbol": symbol, "marginType": "ISOLATED"})
    except Exception:
        pass
    try:
        _futures_signed_request("POST", "/fapi/v1/leverage", {"symbol": symbol, "leverage": lev})
    except Exception:
        pass

    # 2. Fetch live Futures price & exchange filters
    try:
        price_res = _request_with_fixie_retry("GET", f"{FAPI_URL}/fapi/v1/ticker/price", params={"symbol": symbol}, timeout=6).json()
        price = float(price_res.get("price", 0.0))
        if price <= 0:
            return {"error": f"Invalid Futures price for {symbol}"}

        exinfo = _request_with_fixie_retry("GET", f"{FAPI_URL}/fapi/v1/exchangeInfo", timeout=8).json()
        sym_info = next((s for s in exinfo.get("symbols", []) if s.get("symbol") == symbol), None)
        if not sym_info or sym_info.get("status") != "TRADING":
            return {"error": f"{symbol} not tradable on Binance Futures"}

        qty_precision = int(sym_info.get("quantityPrecision", 3))
        min_notional = 5.0
        price_precision = 4
        step_size = 0.0
        for f in sym_info.get("filters", []):
            ft = f.get("filterType")
            if ft == "MIN_NOTIONAL":
                min_notional = max(min_notional, float(f.get("notional", 5.0)))
            elif ft == "LOT_SIZE":
                step_size = float(f.get("stepSize", 0.0))
            elif ft == "PRICE_FILTER":
                tick = f.get("tickSize", "0.0001")
                price_precision = max(0, len(tick.rstrip("0").split(".")[-1])) if "." in tick else 0

        target_notional = clean_collateral * lev
        if target_notional < max(5.20, min_notional):
            return {"error": f"Notional ${target_notional:.2f} below Futures MIN_NOTIONAL ${max(5.20, min_notional):.2f} for {symbol}"}

        raw_qty = target_notional / price
        if step_size > 0:
            import math as _m
            qty = _m.floor(raw_qty / step_size) * step_size
            qty_str = str(int(qty)) if qty_precision == 0 else f"{qty:.{qty_precision}f}"
        elif qty_precision == 0:
            qty = int(raw_qty)
            qty_str = str(qty)
        else:
            qty = round(raw_qty, qty_precision)
            qty_str = f"{qty:.{qty_precision}f}"

        notional = float(qty_str) * price
        if notional < max(5.05, min_notional):
            return {"error": f"Quantized notional ${notional:.2f} < ${max(5.05, min_notional):.2f} for {symbol}"}

        sl_move = abs(float(sl_pct)) / 100.0
        tp_move = abs(float(tp_pct)) / 100.0
        sl_price = round(price * (1.0 + sl_move * 1.15), price_precision)  # safety guard slightly outside soft Guardian floor
        tp_price = round(price * (1.0 - tp_move), price_precision)
    except Exception as e:
        return {"error": f"Failed to calculate Futures params: {e}"}

    # 3. Execute MARKET SELL to open SHORT
    try:
        entry_res = _futures_signed_request("POST", "/fapi/v1/order", {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": qty_str,
        })
        entry_data = entry_res.json()
        if "orderId" not in entry_data:
            return {"error": f"Entry order failed: {entry_data}"}
    except Exception as e:
        return {"error": f"Entry order exception: {e}"}

    # 4. Place exchange safety SL / TP orders AFTER position exists
    time.sleep(0.4)
    for sl_tp_type, stop_px, order_type in [("SL", sl_price, "STOP_MARKET"), ("TP", tp_price, "TAKE_PROFIT_MARKET")]:
        try:
            sl_tp_res = _futures_signed_request("POST", "/fapi/v1/order", {
                "symbol": symbol,
                "side": "BUY",
                "type": order_type,
                "stopPrice": str(stop_px),
                "closePosition": "true",
            })
            print(f"  ✅ Futures {sl_tp_type} safety order: {sl_tp_res.json().get('orderId', sl_tp_res.text)}")
        except Exception as e:
            print(f"  ⚠️ Futures {sl_tp_type} order failed: {e}")

    entry_data["_leverage"] = lev
    entry_data["_collateral_usd"] = clean_collateral
    entry_data["_fallback_price"] = price
    entry_data["_fallback_qty"] = float(qty_str)
    return entry_data


def execute_real_futures_market_close(symbol, quantity=None):
    """Close an active SHORT position, cancel orphan SL/TP orders, and sweep USDT back to Spot."""
    live_pos = next((p for p in get_real_futures_positions() if p.get("symbol") == symbol), None)
    if live_pos:
        live_qty = abs(float(live_pos.get("positionAmt", 0.0)))
        if live_qty > 0:
            quantity = live_qty
    if not quantity or float(quantity) <= 0:
        return {"error": f"No open Futures position quantity found for {symbol}"}

    qty_precision = 3
    try:
        exinfo = _request_with_fixie_retry("GET", f"{FAPI_URL}/fapi/v1/exchangeInfo", timeout=6).json()
        sym_info = next((s for s in exinfo.get("symbols", []) if s.get("symbol") == symbol), None)
        if sym_info:
            qty_precision = int(sym_info.get("quantityPrecision", 3))
    except Exception:
        pass

    qty_str = str(int(float(quantity))) if qty_precision == 0 else f"{float(quantity):.{qty_precision}f}"

    try:
        res = _futures_signed_request("POST", "/fapi/v1/order", {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": qty_str,
            "reduceOnly": "true",
        })
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            try:
                _futures_signed_request("DELETE", "/fapi/v1/allOpenOrders", {"symbol": symbol})
            except Exception:
                pass
            try:
                time.sleep(0.4)
                f_balance = get_real_futures_usdt_balance()
                if f_balance > 0.50:
                    transfer_usdt(max(0.0, round(f_balance - 0.05, 2)), to_futures=False)
            except Exception as te:
                print(f"Error transferring back to spot: {te}")
        return res_json
    except Exception as e:
        return {"error": str(e)}

def calculate_dynamic_proportional_trailing(highest_pnl_pct: float, atr_pct: float, holding_cycles: int = 0, current_pnl_pct: float = 0.0, custom_slack: float = None, symbol: str = None, setup: str = "RS_BREAK", sl_pct_override: float = None, tp_pct_override: float = None):
    """Unified ATR-scaled trailing floor synchronized with validated quant_edge_engine."""
    import quant_edge_engine
    dec = quant_edge_engine.compute_trade_exit_decision(
        highest_pnl_pct=highest_pnl_pct,
        current_pnl_pct=current_pnl_pct,
        atr_pct=max(0.45, float(atr_pct or 1.0)),
        elapsed_minutes=float(holding_cycles * 2),
        setup=setup or "RS_BREAK",
        sl_pct=sl_pct_override,
        tp_pct=tp_pct_override,
    )
    return dec["floor_pct"], dec["phase"], dec["phase_label"]


def quick_position_heartbeat():
    """Sub-second guardian monitoring active real-money LONG (Spot) or SHORT (Futures) position."""
    try:
        state = load_real_account_state()
        pos = state.get("position")
        if not pos or not pos.get("symbol"):
            return None

        sym = pos.get("symbol")
        side = pos.get("side", "LONG")
        is_short = (side == "SHORT")
        qty = float(pos.get("quantity", 0))
        entry = float(pos.get("entry_price", 0))
        if qty <= 0 or entry <= 0:
            return None

        current_price = get_symbol_price(sym, is_futures=is_short)
        if not current_price or current_price <= 0:
            return None

        entry_time_ms = pos.get("entry_time_ms", 0)
        if is_short:
            # For SHORT, best favorable price is the lowest price since entry
            kline_extremum = entry
            try:
                kl_1m = get_klines(sym, "1m", 5)
                if kl_1m:
                    lo_list = [float(k[3]) for k in kl_1m if int(k[0]) >= entry_time_ms - 60000]
                    if lo_list:
                        kline_extremum = min(lo_list)
            except Exception:
                pass
            prev_best = pos.get("highest_price", entry)
            highest_price = min(prev_best if prev_best > 0 else entry, current_price, kline_extremum)
            highest_pnl_pct = ((entry - highest_price) / entry) * 100.0
            current_pnl_pct = ((entry - current_price) / entry) * 100.0
        else:
            kline_high = get_recent_kline_high(sym, limit=5, start_time_ms=entry_time_ms)
            highest_price = max(pos.get("highest_price", entry), current_price, kline_high if kline_high > 0 else current_price)
            highest_pnl_pct = ((highest_price - entry) / entry) * 100.0
            current_pnl_pct = ((current_price - entry) / entry) * 100.0

        current_phase = pos.get("phase", 1)
        atr_1h_pct = pos.get("atr_pct_1h", pos.get("atr_pct_15m", 1.0))
        setup_name = pos.get("setup", "BEAR_SHORT" if is_short else "RS_BREAK")
        sl_override = pos.get("initial_sl_pct")
        tp_override = pos.get("target_tp_pct")
        max_hold_h = float(pos.get("max_hold_hours", 20.0 if setup_name == "DECOUPLED_LEADER" else 24.0))

        import time as _t
        now_ms = _t.time() * 1000.0
        holding_minutes_hb = int((now_ms - entry_time_ms) / 60000.0) if entry_time_ms > 0 else int(pos.get("holding_cycles", 0) * 2)
        pos["holding_cycles"] = holding_minutes_hb // 2

        import quant_edge_engine
        dec = quant_edge_engine.compute_trade_exit_decision(
            highest_pnl_pct=highest_pnl_pct,
            current_pnl_pct=current_pnl_pct,
            atr_pct=atr_1h_pct,
            elapsed_minutes=float(holding_minutes_hb),
            setup=setup_name,
            sl_pct=sl_override,
            tp_pct=tp_override,
            max_hold_hours=max_hold_h,
        )
        sl_pct = dec["floor_pct"]
        new_phase = dec["phase"]
        phase_label = dec["phase_label"]
        should_exit = dec["should_exit"]
        exit_reason = dec["reason"]
        pos["volatility_regime"] = phase_label

        best_improved = (highest_price < pos.get("highest_price", entry)) if is_short else (highest_price > pos.get("highest_price", entry))
        if best_improved or new_phase > current_phase:
            pos["highest_price"] = highest_price
            pos["phase"] = new_phase
            state["position"] = pos
            save_real_account_state(state)

        # Severe systemic BTC crash circuit breaker (> -3% crash from entry) for LONG only
        if not should_exit and not is_short and current_pnl_pct < -2.20 and sym != "BTCUSDT":
            btc_entry = float(pos.get("btc_entry_price", 0.0))
            btc_now = get_symbol_price("BTCUSDT", is_futures=False)
            if btc_entry > 0 and btc_now and ((btc_now - btc_entry) / btc_entry * 100.0) <= -3.00:
                should_exit = True
                exit_reason = f"🚨 ESCUDO FLASH CRASH BTC ({((btc_now-btc_entry)/btc_entry*100.0):+.2f}%)"

        if should_exit:
            print(f"\n🚨 [MICRO-HEARTBEAT] Salida {side} ejecutada para {sym} @ ${current_price:.5f} ({exit_reason})")
            if is_short:
                close_res = execute_real_futures_market_close(sym, qty)
            else:
                close_res = execute_real_spot_market_sell(sym)
                if isinstance(close_res, dict) and close_res.get("code"):
                    close_res = execute_real_spot_market_sell(sym)
            print(f"🔄 Cierre {side} Ejecutado: {close_res}")

            closed_ok = isinstance(close_res, dict) and ("orderId" in close_res or close_res.get("status") == "FILLED")
            if not closed_ok:
                print(f"🚨 [HEARTBEAT] CIERRE FALLIDO - Posición {sym} mantenida.")
                return None

            has_bnb = float(state.get("_cached_bnb_usd", 0.0)) >= 0.05
            net_pnl_pct, fee_pct = quant_edge_engine.compute_net_pnl_after_fees(current_pnl_pct, has_bnb_fee_shield=has_bnb, is_futures=is_short)
            notional_usd = entry * qty
            raw_pnl_usd = ((entry - current_price) * qty) if is_short else ((current_price - entry) * qty)
            pnl_usd = round(raw_pnl_usd - notional_usd * (fee_pct / 100.0), 4)
            is_win_exit = net_pnl_pct > 0.0

            if is_win_exit:
                state["wins"] = state.get("wins", 0) + 1
                state["daily_wins"] = state.get("daily_wins", 0) + 1
                state["_consecutive_losses"] = 0
                state["_last_exit_was_btc_shield"] = False
            else:
                state["losses"] = state.get("losses", 0) + 1
                state["daily_losses"] = state.get("daily_losses", 0) + 1
                state["_consecutive_losses"] = state.get("_consecutive_losses", 0) + 1
                state["_last_loss_time"] = time.time()
                cd_map = state.setdefault("_symbol_side_cooldown", {})
                cd_map[f"{sym}_{side}"] = time.time() + 18 * 3600

            state["trades_count"] = state.get("trades_count", 0) + 1
            state["net_pnl_usd"] = round(state.get("net_pnl_usd", 0.0) + pnl_usd, 4)
            state["_daily_pnl_usd"] = round(state.get("_daily_pnl_usd", 0.0) + pnl_usd, 4)
            state["_last_closed_symbol"] = sym
            state["_last_closed_time"] = time.time()
            state["_last_exit_price"] = current_price
            state["last_trade_time"] = datetime.now().strftime("%y-%m-%d<br>%H:%M")

            pos_snap = dict(pos)
            try:
                import learning_engine
                trade_ctx = {
                    "score": pos_snap.get("score", 85),
                    "rsi_15m": pos_snap.get("rsi_15m", 50.0),
                    "atr_pct_15m": pos_snap.get("atr_pct_15m", atr_1h_pct),
                    "vol_surge": pos_snap.get("vol_surge", 1.0),
                    "vol_surge_1m": pos_snap.get("vol_surge_1m", 1.0),
                    "fii_score": pos_snap.get("fii_score", 60),
                    "obv_trend": pos_snap.get("obv_trend", "ACCUMULATING"),
                    "macro_trend_4h": pos_snap.get("macro_regime", "NEUTRAL"),
                }
                learning_engine.record_trade_outcome(
                    symbol=sym,
                    side=side,
                    entry_price=entry,
                    exit_price=current_price,
                    pnl_usd=pnl_usd,
                    result_type="WIN" if is_win_exit else "LOSS",
                    notes=f"Real {side} exited via {exit_reason} (Bruto: {current_pnl_pct:+.2f}%, Fee: -{fee_pct:.2f}%, Neto: {net_pnl_pct:+.2f}%)",
                    account_id="R-01",
                    group_name="CUENTA REAL",
                    context=trade_ctx,
                )
            except Exception as le_err:
                print(f"⚠️ Learning Engine registro fallido: {le_err}")

            state["position"] = None
            state["status"] = f"{'🟢 WIN' if is_win_exit else '🔴 LOSS'} Cerrado ({sym} {side} Neto: {net_pnl_pct:+.2f}% / ${pnl_usd:+.4f})"
            save_real_account_state(state)
            try:
                diagnose_full_spot_wallet()
            except Exception:
                pass
            return "EXIT"

        return {
            "symbol": sym,
            "side": side,
            "price": current_price,
            "pnl_pct": current_pnl_pct,
            "highest_pnl": highest_pnl_pct,
            "phase": new_phase,
            "sl_pct": sl_pct,
            "entry_price": entry,
            "phase_label": phase_label,
        }
    except Exception:
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
    global _trade_executed_this_cycle
    executed_trade = False
    state = load_real_account_state()
    import math

    # ═══ PROTECCIÓN: Solo 1 trade real por ciclo de pipeline ═══
    # Evita que múltiples candidatos abran posiciones en paralelo en el mismo ciclo
    if best_symbol and not is_bearish:
        if _trade_executed_this_cycle:
            print(f"🔒 [1 TRADE/CICLO] Ya se ejecutó 1 trade real este ciclo. {best_symbol} queda en cola para el próximo ciclo.")
            return
    
    # Null guard on current_price
    if not current_price or current_price <= 0:
        current_price = 1.0

    
    # AUTOMATIC COMPOUND INTEREST ALLOCATION (SPOT LONG OR FUTURES SHORT - 1 POSITION AT A TIME)
    import quant_edge_engine as _qee
    raw_usdt = float(state.get("_cached_usdt_free", state.get("current_balance_usd", 0.0)) or 0.0)
    # Use clean 2-decimal precision minus tiny $0.05 safety margin (e.g. $5.95 -> $5.90 usable above $5.10 MIN_NOTIONAL)
    usdt_free = max(0.0, math.floor(max(0.0, raw_usdt - 0.05) * 100.0) / 100.0)

    # 🟡 PROTECCIÓN ESCUDO BNB (Solo convierte exceso de BNB >= $5.50; conserva 0.0012 BNB para 25% dto fee)
    if usdt_free < 5.10 and not state.get("position"):
        try:
            live_bals = get_real_balances()
            live_bnb_qty = 0.0
            for _b in live_bals or []:
                if _b.get("asset") == "BNB":
                    live_bnb_qty = float(_b.get("free", 0))
                    break
            bnb_curr_px = get_symbol_price("BNBUSDT", is_futures=False) or 550.0
            bnb_total_usd = live_bnb_qty * bnb_curr_px
            if bnb_total_usd >= 6.50:
                bnb_reserve_qty = 0.0020  # Mantener escudo BNB comisiones
                bnb_convert_qty = max(0.0, live_bnb_qty - bnb_reserve_qty)
                if bnb_convert_qty * bnb_curr_px >= 5.10:
                    print(f"🟡 [AUTO-LIQUIDEZ BNB] Convirtiendo excedente {bnb_convert_qty:.4f} BNB a USDT...")
                    execute_real_spot_market_sell("BNBUSDT", bnb_convert_qty)
                    import time as _t_liq
                    _t_liq.sleep(1.0)
                    state = diagnose_full_spot_wallet()
                    raw_usdt = float(state.get("_cached_usdt_free", 0.0) or 0.0)
                    usdt_free = max(0.0, math.floor(max(0.0, raw_usdt - 0.05) * 100.0) / 100.0)
        except Exception as _e_conv:
            print(f"⚠️ Nota auto-liquidez BNB: {_e_conv}")

    active_pos_state = state.get("position") if isinstance(state.get("position"), dict) and state.get("position", {}).get("symbol") else None
    crypto_balances = []
    if active_pos_state and active_pos_state.get("side", "LONG") == "LONG":
        qty = active_pos_state.get("quantity", active_pos_state.get("cost_usd", 10.0) / max(active_pos_state.get("entry_price", 1.0), 0.0001))
        crypto_balances = [{"asset": active_pos_state["symbol"].replace("USDT", ""), "free": qty}]

    # --- LEARNING ENGINE INTEGRATION ---
    market_bias = None
    try:
        import learning_engine
        market_bias = learning_engine.get_market_bias()
    except Exception:
        pass

    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")

    # ========================================
    # CASE 1: We have an active LONG (Spot) or SHORT (Futures) position
    # ========================================
    if active_pos_state:
        active_symbol = active_pos_state["symbol"]
        active_side = active_pos_state.get("side", "LONG")
        is_short_pos = (active_side == "SHORT")
        active_asset = active_symbol.replace("USDT", "")
        active_qty = float(active_pos_state.get("quantity", 0.0) or (crypto_balances[0]["free"] if crypto_balances else 0.0))

        import multi_timeframe_analyzer
        if not is_short_pos and (multi_timeframe_analyzer.is_stablecoin(active_symbol) or active_symbol == "UUSDT"):
            print(f"🚨 DETECTADA POSICIÓN EN STABLECOIN ({active_symbol}). Venta de Emergencia...")
            execute_real_spot_market_sell(active_symbol, active_qty)
            state["position"] = None
            state["status"] = "🟦 Buscando Entrada A+"
            save_real_account_state(state)
            return state

        active_current_price = get_symbol_price(active_symbol, is_futures=is_short_pos)
        if not active_current_price:
            active_current_price = current_price

        entry = float(active_pos_state.get("entry_price", active_current_price))
        if entry <= 0:
            entry = active_current_price
        pnl_pct = ((entry - active_current_price) / entry * 100.0) if is_short_pos else ((active_current_price - entry) / entry * 100.0)
        pnl_usd = ((entry - active_current_price) * active_qty) if is_short_pos else ((active_current_price - entry) * active_qty)

        _entry_time_ms = active_pos_state.get("entry_time_ms", 0)
        if is_short_pos:
            kline_extremum = entry
            try:
                _kl_s = get_klines(active_symbol, "1m", 5)
                if _kl_s:
                    _lo_s = [float(k[3]) for k in _kl_s if int(k[0]) >= _entry_time_ms - 60000]
                    if _lo_s:
                        kline_extremum = min(_lo_s)
            except Exception:
                pass
            prev_hp = active_pos_state.get("highest_price", entry)
            highest_price = min(prev_hp if prev_hp > 0 else entry, active_current_price, kline_extremum)
            highest_pnl_pct = ((entry - highest_price) / entry * 100.0)
        else:
            kline_high = get_recent_kline_high(active_symbol, limit=5, start_time_ms=_entry_time_ms)
            highest_price = max(active_pos_state.get("highest_price", entry), active_current_price, kline_high if kline_high > 0 else active_current_price)
            highest_pnl_pct = ((highest_price - entry) / entry * 100.0)

        holding_cycles = active_pos_state.get("holding_cycles", 0) + 1
        real_holding_minutes = int((time.time() * 1000.0 - _entry_time_ms) / 60000.0) if _entry_time_ms > 0 else int(holding_cycles * 2)
        atr_1h_pct = float(active_pos_state.get("atr_pct_1h", active_pos_state.get("atr_pct_15m", 1.0)))
        setup_name = active_pos_state.get("setup", "BEAR_SHORT" if is_short_pos else "RS_BREAK")

        dec = _qee.compute_trade_exit_decision(
            highest_pnl_pct=highest_pnl_pct,
            current_pnl_pct=pnl_pct,
            atr_pct=atr_1h_pct,
            elapsed_minutes=float(real_holding_minutes),
            setup=setup_name,
            sl_pct=active_pos_state.get("initial_sl_pct"),
            tp_pct=active_pos_state.get("target_tp_pct"),
            max_hold_hours=float(active_pos_state.get("max_hold_hours", 20.0 if setup_name == "DECOUPLED_LEADER" else 24.0)),
        )
        trailing_floor_pct = dec["floor_pct"]
        phase = dec["phase"]
        phase_msg = dec["phase_label"]
        should_exit = dec["should_exit"]
        reason_str = dec["reason"]

        if not should_exit and not is_short_pos and pnl_pct < -2.20 and active_symbol != "BTCUSDT":
            btc_entry_px = float(active_pos_state.get("btc_entry_price", 0.0))
            btc_price_now = get_symbol_price("BTCUSDT", is_futures=False)
            if btc_entry_px > 0 and btc_price_now and ((btc_price_now - btc_entry_px) / btc_entry_px * 100.0) <= -3.00:
                should_exit = True
                reason_str = f"🚨 ESCUDO FLASH CRASH BTC ({((btc_price_now-btc_entry_px)/btc_entry_px*100.0):+.2f}%)"

        sl_target = entry * (1.0 - trailing_floor_pct / 100.0) if is_short_pos else entry * (1.0 + trailing_floor_pct / 100.0)

        active_pos_state.update({
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "highest_price": highest_price,
            "cost_usd": round(active_qty * entry, 2),
            "side": active_side,
            "phase": phase,
            "holding_cycles": holding_cycles,
            "volatility_regime": phase_msg,
        })
        state["position"] = active_pos_state
        price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
        state["status"] = f"🔵 En Vivo {active_side} ({active_symbol} @ {price_fmt(active_current_price)})"

        print("\n" + "="*65)
        print(f"📊 [SEGUIMIENTO DE POSICIÓN ACTIVA REAL - {active_side}]")
        print(f"🪙 Moneda: {active_symbol} | Qty: {active_qty:,.4f} | Tiempo: {real_holding_minutes}m / {int(dec['max_hold_hours']*60)}m")
        print(f"💵 Entrada: {price_fmt(entry)} | Extremo Favorable: {price_fmt(highest_price)} (+{highest_pnl_pct:.2f}%)")
        print(f"📈 PnL Bruto Actual: {pnl_pct:+.2f}% (${pnl_usd:+.4f} USD)")
        print(f"🧠 {phase_msg}")
        print(f"🛡️ Piso Salida: {price_fmt(sl_target)} ({trailing_floor_pct:+.2f}%) | TP: +{dec['tp_pct']:.2f}%")
        print("="*65 + "\n")

        if entry > 0 and should_exit:
            print(f"🎯 ALERTA REAL: Salida {active_side} por {reason_str} en {active_symbol}...")
            try:
                res_json = execute_real_futures_market_close(active_symbol, active_qty) if is_short_pos else execute_real_spot_market_sell(active_symbol)
                if isinstance(res_json, dict) and ("orderId" in res_json or res_json.get("status") == "FILLED"):
                    has_bnb = float(state.get("_cached_bnb_usd", 0.0)) >= 0.05
                    net_pnl_pct, fee_pct = _qee.compute_net_pnl_after_fees(pnl_pct, has_bnb_fee_shield=has_bnb, is_futures=is_short_pos)
                    raw_pnl_usd = ((entry - active_current_price) * active_qty) if is_short_pos else ((active_current_price - entry) * active_qty)
                    pnl_usd = round(raw_pnl_usd - (entry * active_qty) * (fee_pct / 100.0), 4)

                    from datetime import timezone as _tz
                    today_str = datetime.now(_tz.utc).strftime("%Y-%m-%d")
                    if state.get("last_daily_reset_date") != today_str or state.get("_daily_pnl_date") != today_str:
                        state["daily_wins"] = 0
                        state["daily_losses"] = 0
                        state["_consecutive_losses"] = 0
                        state["_daily_pnl_usd"] = 0.0
                        state["_daily_pnl_date"] = today_str
                        state["last_daily_reset_date"] = today_str

                    state["last_trading_day"] = today_str
                    is_win_exit = net_pnl_pct > 0.0
                    if is_win_exit:
                        state["wins"] = state.get("wins", 0) + 1
                        state["daily_wins"] = state.get("daily_wins", 0) + 1
                        state["_consecutive_losses"] = 0
                        res_type = "WIN"
                    else:
                        state["losses"] = state.get("losses", 0) + 1
                        state["daily_losses"] = state.get("daily_losses", 0) + 1
                        state["_consecutive_losses"] = state.get("_consecutive_losses", 0) + 1
                        state["_last_loss_time"] = time.time()
                        cd_map = state.setdefault("_symbol_side_cooldown", {})
                        cd_map[f"{active_symbol}_{active_side}"] = time.time() + 18 * 3600
                        res_type = "LOSS"

                    state["trades_count"] = state.get("trades_count", 0) + 1
                    state["_daily_pnl_usd"] = round(state.get("_daily_pnl_usd", 0.0) + pnl_usd, 4)
                    state["_daily_pnl_date"] = today_str
                    pos_snap = dict(active_pos_state)
                    state["position"] = None
                    state["status"] = f"{'🟢 WIN' if is_win_exit else '🔴 STOP'} Cerrado ({active_symbol} {active_side} Neto: {net_pnl_pct:+.2f}% / ${pnl_usd:+.4f})"
                    state["_last_closed_symbol"] = active_symbol
                    state["_last_closed_time"] = time.time()
                    state["_last_exit_price"] = active_current_price
                    state["last_trade_time"] = now_str
                    save_real_account_state(state)

                    try:
                        diagnose_full_spot_wallet()
                    except Exception:
                        pass

                    try:
                        import learning_engine
                        trade_ctx = {
                            "score": pos_snap.get("score", 85),
                            "rsi_15m": pos_snap.get("rsi_15m", 50.0),
                            "atr_pct_15m": pos_snap.get("atr_pct_15m", atr_1h_pct),
                            "vol_surge": pos_snap.get("vol_surge", 1.0),
                            "vol_surge_1m": pos_snap.get("vol_surge_1m", 1.0),
                            "fii_score": pos_snap.get("fii_score", 60),
                            "obv_trend": pos_snap.get("obv_trend", "ACCUMULATING"),
                            "macro_trend_4h": pos_snap.get("macro_regime", "NEUTRAL"),
                        }
                        learning_engine.record_trade_outcome(
                            symbol=active_symbol, side=active_side, entry_price=entry, exit_price=active_current_price,
                            pnl_usd=pnl_usd, result_type=res_type,
                            notes=f"Real {active_side} exited via {reason_str} (Bruto: {pnl_pct:+.2f}%, Fee: -{fee_pct:.2f}%, Neto: {net_pnl_pct:+.2f}%)",
                            account_id="R-01", group_name="CUENTA REAL", context=trade_ctx
                        )
                    except Exception as le:
                        print(f"Learning engine error: {le}")

                    print(f"✅ {active_side} cerrado exitosamente: {res_type} (Neto {net_pnl_pct:+.2f}% | ${pnl_usd:+.4f})")
                else:
                    print(f"⚠️ Cierre {active_side} rechazado: {res_json}")
            except Exception as e:
                print(f"Error ejecutando cierre real {active_side}: {e}")
                    
    # ========================================
    # CASE 2: No active position - Look for SPOT LONG Entry (15-FINALIST CASCADE)
    # ========================================
    else:
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+ (Modo Francotirador)"
        check_and_apply_utc_daily_reset(state)
        
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
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 80)
        # Época de oro Sep 14-22: Solo candidatos de confluencia institucional A+ (Score >= 85)
        min_required_score = max(85, real_long_score) if not is_learned_signal else 80
        
        # Check learning engine bias before entering
        if market_bias:
            bias_direction = market_bias.get("recommended_bias", "NEUTRAL")
            if bias_direction == "STRONG_SHORT":
                print(f"⚠️ [LEARNING ENGINE] Sesgo de mercado: {bias_direction} (Exigiendo confluencia A+ estricta en los 67 pares del Top 100 CMC)")
            
        # ═════════════════════════════════════════════════════════════════════════
        # 🧬 ANÁLISIS EN CASCADA DE ADN ACTIVO PARA LOS 67 PARES DEL TOP 100 CMC:
        # Evalúa en orden de calidad institucional hasta encontrar el ganador 100% A+
        # ═════════════════════════════════════════════════════════════════════════
        candidate_queue = []
        if best_symbol and best_symbol != "NONE":
            top_qe = None
            top_side = "LONG"
            if candidates_list:
                m_top = next((c for c in candidates_list if c.get("symbol") == best_symbol), None)
                if m_top and isinstance(m_top.get("quant_edge"), dict):
                    top_qe = m_top["quant_edge"]
                    top_side = top_qe.get("side", "LONG")
            candidate_queue.append({
                "symbol": best_symbol,
                "score": best_score,
                "price": current_price,
                "is_ai_champion": is_learned_signal,
                "side": top_side,
                "quant_edge": top_qe,
            })

        if candidates_list:
            for c in candidates_list[:3]:
                csym = c.get("symbol")
                c_qe = c.get("quant_edge") if isinstance(c.get("quant_edge"), dict) else None
                c_side = c_qe.get("side", "LONG") if c_qe else ("SHORT" if c.get("suggested_action") == "SELL_SHORT" else "LONG")
                if not is_learned_signal or c_qe:
                    if csym and csym not in [q["symbol"] for q in candidate_queue]:
                        cscore = c.get("score", 50)
                        cprice = (c_qe.get("price") if c_qe else 0.0) or c.get("tech_data", {}).get("current_price", 0.0)
                        candidate_queue.append({
                            "symbol": csym,
                            "score": cscore,
                            "price": cprice,
                            "is_ai_champion": False,
                            "side": c_side,
                            "quant_edge": c_qe,
                        })
        
        if not candidate_queue:
            return

        # ═══════════════════════════════════════════════════════════════════════
        # 🛡️ ESCUDO 1: CIRCUIT BREAKER DE RACHAS PERDEDORAS
        # Si perdemos 2 trades consecutivos → pausa 25 minutos antes del siguiente.
        # Rachas de pérdida = condiciones de mercado adversas, no error del bot.
        # ═══════════════════════════════════════════════════════════════════════
        consec_losses = state.get("_consecutive_losses", 0)
        last_loss_time = state.get("_last_loss_time", 0)
        if consec_losses >= 2:
            minutes_since_loss = (time.time() - last_loss_time) / 60.0
            cooldown_needed = 45.0  # 45 min cooling tras 2 pérdidas consecutivas
            if minutes_since_loss < cooldown_needed:
                remaining = cooldown_needed - minutes_since_loss
                print(f"🛑 [CIRCUIT BREAKER RACHA] {consec_losses} pérdidas consecutivas. Enfriamiento: {remaining:.0f}m restantes.")
                return
            else:
                print(f"✅ [CIRCUIT BREAKER] Cooldown completado ({minutes_since_loss:.0f}m). Reactivando búsqueda A+.")
                state["_consecutive_losses"] = 0
                save_real_account_state(state)

        # FIX CRITICO: Circuit Breaker basado en LOSSES DEL DÍA
        # Si hay 1 pérdida hoy → cooldown preventivo de 30 min (evita re-entrar en la misma ola correctiva)
        # Si hay >= 2 pérdidas hoy → cooldown estricto de 60 min (protección de capital en día adverso)
        _daily_l = state.get("daily_losses", 0)
        _last_loss_ts = state.get("_last_loss_time", 0)
        if _daily_l >= 1 and _last_loss_ts > 0:
            _mins_since = (time.time() - _last_loss_ts) / 60.0
            _needed_cb = 60.0 if _daily_l >= 2 else 30.0
            if _mins_since < _needed_cb:
                _remaining = _needed_cb - _mins_since
                print(f"🛑 [CB DIARIO] {_daily_l} pérdida(s) hoy. Cooldown de seguridad: {_remaining:.0f}m restantes. Esperando condiciones más favorables.")
                return

        # ═══════════════════════════════════════════════════════════════════════
        # 🛡️ ESCUDO 2: LÍMITE DIARIO DE PÉRDIDA (Daily Loss Limit)
        # Máximo $0.60 de pérdida neta en el día. Si se supera → STOP por hoy.
        # Protege el capital de días de mercado adverso sostenido.
        # ═══════════════════════════════════════════════════════════════════════
        try:
            check_and_apply_utc_daily_reset(state)
            from datetime import datetime as _dt, timezone as _tz_mod
            today_str = _dt.now(_tz_mod.utc).strftime("%Y-%m-%d")
            daily_pnl = state.get("_daily_pnl_usd", 0.0)
            daily_loss_limit = -0.60  # Max $0.60 loss per day (protege cuenta pequeña de $10 USD)
            if daily_pnl <= daily_loss_limit:
                print(f"🛑 [LÍMITE DIARIO] Pérdida acumulada hoy ({today_str} UTC): ${daily_pnl:.3f}. Límite: ${daily_loss_limit}. Operaciones pausadas hasta mañana. Preservando capital.")
                return
            elif daily_pnl < -0.30:
                print(f"⚠️ [ALERTA DIARIA] Pérdida acumulada hoy ({today_str} UTC): ${daily_pnl:.3f}. Cerca del límite diario. Modo ultra-selectivo activado.")

            # 🏆 CANDADO DE META DIARIA CUMPLIDA (≥ +1.0% NETO LIBRE DE COMISIONES)
            _cur_bal = state.get("current_balance_usd", 12.0)
            _target_goal_usd = round(_cur_bal * 0.01, 4)  # 1% del balance
            if daily_pnl >= _target_goal_usd and daily_pnl > 0.0001:
                print(f"🏆 [META DIARIA CUMPLIDA] PnL hoy ({state.get('_daily_pnl_date', today_str)} UTC): +${daily_pnl:.4f} USD >= +${_target_goal_usd:.4f} USD (≥ +1.0% neto libre de comisiones).")
                print(f"   Ganancia diaria blindada. Capital protegido hasta las 00:00:00 UTC.")
                return

            # 🛑 LÍMITE MÁXIMO DE TRADES DIARIOS ADAPTATIVO:
            # · Día ganador (PnL > 0): hasta 6 trades — el sistema está demostrando precisión ese día.
            # · Día neutral o en rojo (PnL <= 0): máximo 4 trades — modo francotirador para proteger capital.
            _daily_trades = state.get("daily_wins", 0) + state.get("daily_losses", 0)
            _max_daily_trades = 6 if daily_pnl > 0 else 4
            if _daily_trades >= _max_daily_trades:
                print(f"🛑 [LÍMITE TRADES DIARIOS] Ya se ejecutaron {_daily_trades}/{_max_daily_trades} trades hoy ({today_str} UTC) (PnL: ${daily_pnl:+.4f}). {'Día ganador → máx 6 trades.' if daily_pnl > 0 else 'Día en rojo → máx 4 trades (modo conservador).'}")
                return

        except Exception:
            pass


        # ═══════════════════════════════════════════════════════════════════════
        # 🛡️ ESCUDO 3: SISMÓGRAFO DE AMPLITUD & COOLDOWN QUANT (SOLO PARA LONG)
        # En BEAR_SHORT (mercado bajista confirmado), las caídas de BTC son la tesis del SHORT.
        # ═══════════════════════════════════════════════════════════════════════
        has_short_cand = any(c.get("side") == "SHORT" for c in candidate_queue)
        has_quant_cand = any(isinstance(c.get("quant_edge"), dict) for c in candidate_queue)

        if not has_short_cand:
            try:
                breadth_symbols = ["ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
                                   "DOTUSDT", "LINKUSDT", "LTCUSDT", "AVAXUSDT", "POLUSDT"]
                bearish_count = 0
                lower_wicks = []
                drop_pcts = []

                for bsym in breadth_symbols:
                    bkl = get_klines(bsym, "15m", 2)
                    if bkl and len(bkl) >= 1:
                        bc = float(bkl[-1][4]); bo = float(bkl[-1][1])
                        bh = float(bkl[-1][2]); bl = float(bkl[-1][3])
                        rng = bh - bl
                        wick_pct = ((min(bo, bc) - bl) / rng * 100.0) if rng > 0 else 0.0
                        lower_wicks.append(wick_pct)
                        drop_pcts.append(((bc - bo) / bo * 100.0) if bo > 0 else 0.0)
                        if bc < bo:
                            bearish_count += 1

                avg_wick_pct = (sum(lower_wicks) / len(lower_wicks)) if lower_wicks else 0.0
                avg_drop_pct = (sum(drop_pcts) / len(drop_pcts)) if drop_pcts else 0.0
                is_genuine_market_panic = bool(bearish_count >= 7 and avg_drop_pct <= -1.20 and avg_wick_pct < 25.0)
                if is_genuine_market_panic and not has_quant_cand:
                    print(f"🛑 [AMPLITUD DINÁMICA: PÁNICO REAL] {bearish_count}/10 alts cayendo ({avg_drop_pct:+.2f}%). USDT protegido.")
                    return
                state["_breadth_warning"] = bool(bearish_count >= 6)
            except Exception:
                state["_breadth_warning"] = False

            try:
                btc_1h_kl = get_klines("BTCUSDT", "1h", 25)
                if btc_1h_kl and len(btc_1h_kl) >= 22:
                    c1h_now = float(btc_1h_kl[-1][4]); o1h_now = float(btc_1h_kl[-1][1])
                    btc_1h_pct = ((c1h_now - o1h_now) / o1h_now) * 100.0 if o1h_now > 0 else 0.0
                    if btc_1h_pct <= -0.95:
                        print(f"🛑 [GUARDIÁN BITCOIN 1H] BTC en caída violenta 1H ({btc_1h_pct:+.2f}%). Prohibido abrir LONG.")
                        return

                btc_kl = get_klines("BTCUSDT", "5m", 3)
                if btc_kl and len(btc_kl) >= 2:
                    c_now = float(btc_kl[-1][4]); o_now = float(btc_kl[-1][1])
                    btc_5m_pct = ((c_now - o_now) / o_now) * 100.0 if o_now > 0 else 0.0
                    if btc_5m_pct <= -0.65:
                        print(f"🛑 [GUARDIÁN BITCOIN 5M] BTC en flash drop 5M ({btc_5m_pct:+.2f}%). Prohibido abrir LONG.")
                        return
            except Exception:
                pass

        # Circuit breaker diario por pérdidas reales consecutivas
        try:
            _daily_losses = state.get("daily_losses", 0)
            _daily_pnl = state.get("_daily_pnl_usd", 0.0)
            if _daily_losses >= 3 and _daily_pnl <= -0.35:
                print(f"🔴 [CIRCUIT BREAKER DIARIO] {_daily_losses} pérdidas hoy (PnL: ${_daily_pnl:+.4f}). Pausa hasta mañana UTC.")
                return
        except Exception:
            pass

        total_cands = len(candidate_queue)
        print(f"\n🔬 [EJECUCIÓN DE PRECISIÓN A+] Evaluando {total_cands} finalistas seleccionados...")

        executed_trade = False
        import adaptive_asset_dna
        import multi_timeframe_analyzer
        import orderbook_analyzer

        last_closed_sym = state.get("_last_closed_symbol")
        last_closed_time = state.get("_last_closed_time", 0)
        last_exit_price = state.get("_last_exit_price", 0.0)
        now_epoch = time.time()
        cd_map = state.get("_symbol_side_cooldown", {})

        for cand_idx, cand_info in enumerate(candidate_queue, 1):
            cand_sym = cand_info["symbol"]
            cand_score = cand_info["score"]
            cand_price = cand_info["price"]
            cand_side = cand_info.get("side", "LONG")
            qe_sig = cand_info.get("quant_edge") if isinstance(cand_info.get("quant_edge"), dict) else None
            is_ai_top = cand_info.get("is_ai_champion", False)
            sym_clean = cand_sym.replace("USDT", "")

            if sym_clean in stablecoins_blacklist or cand_sym in stablecoins_blacklist:
                continue

            # Cooldown cuantitativo de 18h tras pérdida en el mismo (símbolo, dirección)
            if float(cd_map.get(f"{cand_sym}_{cand_side}", 0.0)) > now_epoch:
                rem_h = (float(cd_map[f"{cand_sym}_{cand_side}"]) - now_epoch) / 3600.0
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym} {cand_side}] Cooldown post-loss ({rem_h:.1f}h restantes).")
                continue

            try:
                import quant_database
                is_quar_sql, quar_sql_msg = quant_database.is_symbol_in_quarantine(cand_sym)
                if is_quar_sql:
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] En Cuarentena SQLite: {quar_sql_msg}")
                    continue
            except Exception:
                pass

            if not cand_price or cand_price <= 0:
                cand_price = get_symbol_price(cand_sym, is_futures=(cand_side == "SHORT"))
                if not cand_price or cand_price <= 0:
                    continue

            # ⚡ RUTA DIRECTA VALIDADA QUANT EDGE (RS_BREAK / DECOUPLED_LEADER / BEAR_SHORT)
            if qe_sig is not None:
                ob_info = orderbook_analyzer.fetch_orderbook_depth(cand_sym, limit=20)
                spread_now = ob_info.get("spread_pct", 0.0)
                bid_vol = ob_info.get("bid_vol_usdt", 0.0)
                if spread_now > 0.35:
                    print(f"  ⛔ [{cand_sym}] Spread excesivo ({spread_now:.3f}% > 0.35%).")
                    continue
                if bid_vol < 8000.0 and spread_now > 0.15:
                    print(f"  ⛔ [{cand_sym}] Liquidez delgada (Bids=${bid_vol:,.0f}).")
                    continue

                # Proteger Spot LONG ante caída instantánea 1M de BTC
                if cand_side == "LONG":
                    try:
                        _b1m = get_klines("BTCUSDT", "1m", 2)
                        if _b1m and float(_b1m[-1][1]) > 0:
                            _b1_ret = (float(_b1m[-1][4]) - float(_b1m[-1][1])) / float(_b1m[-1][1]) * 100.0
                            if _b1_ret < -0.60:
                                print(f"  🛑 [PRE-BUY 1M GATE] BTC caída súbita {_b1_ret:+.2f}%. Esperando estabilización.")
                                continue
                    except Exception:
                        pass

                try:
                    live_diag = diagnose_full_spot_wallet()
                    live_usdt = float(live_diag.get("_cached_usdt_free", 0.0) or 0.0)
                    usdt_free = max(0.0, math.floor(max(0.0, live_usdt - 0.05) * 100.0) / 100.0)
                except Exception:
                    pass

                if usdt_free < 5.10:
                    print(f"  ⚠️ [PRE-FLIGHT] Saldo libre ${usdt_free:.2f} USDT < $5.10 mínimo Binance. Operación omitida.")
                    return state

                atr_1h = float(qe_sig.get("atr_pct", 1.0))
                sl_pct_q = float(qe_sig.get("sl_pct", -1.80))
                tp_pct_q = float(qe_sig.get("tp_pct", 3.20))
                max_hold_h_q = float(qe_sig.get("max_hold_hours", 24.0))
                setup_q = qe_sig.get("setup", "RS_BREAK")

                print(f"\n💎 [SEÑAL CUÁNTICA VALIDADA: {setup_q} | {cand_side}] {cand_sym} @ ${cand_price:.4f} | RS8={qe_sig.get('rs_8h_pct',0):+.1f}% Vol={qe_sig.get('vol_surge',1):.2f}x Taker={qe_sig.get('taker_buy_pct',50):.1f}% SL={sl_pct_q:.2f}% TP=+{tp_pct_q:.2f}%")

                if cand_side == "SHORT":
                    if not is_futures_trading_enabled():
                        print(f"  🛡️ [FUTURES DESHABILITADO] {cand_sym} SHORT omitido: cuenta sin permisos USD-M Futures. Capital USDT preservado en Spot.")
                        continue
                    print(f"🚀 [ORDEN FUTUROS SHORT 2x ISOLATED] Abriendo SHORT en {cand_sym} con colateral ${usdt_free:.2f} USDT...")
                    sh_res = execute_real_futures_market_short(cand_sym, usdt_free, leverage=2, sl_pct=sl_pct_q, tp_pct=tp_pct_q)
                    if isinstance(sh_res, dict) and ("orderId" in sh_res or sh_res.get("status") == "FILLED"):
                        time.sleep(0.5)
                        live_fpos = next((p for p in get_real_futures_positions() if p.get("symbol") == cand_sym), None)
                        actual_ep = float(live_fpos.get("entryPrice", 0.0)) if live_fpos else 0.0
                        actual_qty = abs(float(live_fpos.get("positionAmt", 0.0))) if live_fpos else 0.0
                        if actual_ep <= 0:
                            actual_ep = float(sh_res.get("avgPrice") or sh_res.get("_fallback_price") or cand_price)
                        if actual_qty <= 0:
                            actual_qty = float(sh_res.get("executedQty") or sh_res.get("_fallback_qty") or round((usdt_free * 2.0) / actual_ep, 4))
                        state["position"] = {
                            "symbol": cand_sym,
                            "entry_price": actual_ep,
                            "cost_usd": round(actual_qty * actual_ep, 2),
                            "collateral_usd": round(usdt_free, 2),
                            "leverage": int(sh_res.get("_leverage", 2)),
                            "side": "SHORT",
                            "setup": setup_q,
                            "quantity": actual_qty,
                            "highest_price": actual_ep,
                            "phase": 1,
                            "initial_sl_pct": sl_pct_q,
                            "target_tp_pct": tp_pct_q,
                            "max_hold_hours": max_hold_h_q,
                            "atr_pct_1h": atr_1h,
                            "atr_pct_15m": atr_1h,
                            "score": int(qe_sig.get("score", cand_score)),
                            "vol_surge": float(qe_sig.get("vol_surge", 1.25)),
                            "obv_trend": "DISTRIBUTING",
                            "macro_regime": qe_sig.get("macro_regime", "BEAR_CRASH"),
                            "entry_time_ms": int(time.time() * 1000),
                            "btc_entry_price": get_symbol_price("BTCUSDT", is_futures=False) or 0.0,
                        }
                        state["status"] = f"🔴 En Vivo SHORT ({cand_sym} @ ${actual_ep:.4f})"
                        state["_cached_usdt_free"] = 0.0
                        state["last_trade_time"] = now_str
                        save_real_account_state(state)
                        _trade_executed_this_cycle = True
                        executed_trade = True
                        print(f"✅ FUTURES SHORT abierto: {cand_sym} ({actual_qty} @ ${actual_ep:.4f})")
                        break
                    else:
                        print(f"  ⚠️ Futures SHORT rechazado en {cand_sym}: {sh_res}")
                        continue
                else:
                    print(f"🚀 [ORDEN SPOT LONG] Enviando compra en {cand_sym} con ${usdt_free:.2f} USDT...")
                    buy_res = execute_real_spot_market_buy(cand_sym, usdt_free)
                    if isinstance(buy_res, dict) and ("orderId" in buy_res or buy_res.get("status") == "FILLED"):
                        time.sleep(0.5)
                        exact_entry, exact_cost, exact_qty = get_exact_real_entry_price(cand_sym)
                        qty = exact_qty if exact_qty else float(buy_res.get("executedQty", 0))
                        cum_quote = exact_cost if exact_cost else float(buy_res.get("cummulativeQuoteQty", 0))
                        actual_ep = exact_entry or (round(cum_quote / qty, 8) if qty > 0 and cum_quote > 0 else cand_price)
                        actual_cost = exact_cost or (round(cum_quote, 2) if cum_quote > 0 else round(usdt_free, 2))
                        if qty <= 0:
                            qty = round(usdt_free / actual_ep, 5)
                        state["position"] = {
                            "symbol": cand_sym,
                            "entry_price": actual_ep,
                            "cost_usd": actual_cost,
                            "side": "LONG",
                            "setup": setup_q,
                            "quantity": qty,
                            "highest_price": actual_ep,
                            "phase": 1,
                            "initial_sl_pct": sl_pct_q,
                            "target_tp_pct": tp_pct_q,
                            "max_hold_hours": max_hold_h_q,
                            "atr_pct_1h": atr_1h,
                            "atr_pct_15m": atr_1h,
                            "score": int(qe_sig.get("score", cand_score)),
                            "vol_surge": float(qe_sig.get("vol_surge", 1.25)),
                            "obv_trend": "ACCUMULATING",
                            "macro_regime": qe_sig.get("macro_regime", "BULL"),
                            "entry_time_ms": int(time.time() * 1000),
                            "btc_entry_price": get_symbol_price("BTCUSDT", is_futures=False) or 0.0,
                        }
                        state["status"] = f"🔵 En Vivo LONG ({cand_sym} @ ${actual_ep:.4f})"
                        state["_cached_usdt_free"] = 0.0
                        state["last_trade_time"] = now_str
                        save_real_account_state(state)
                        _trade_executed_this_cycle = True
                        executed_trade = True
                        print(f"✅ SPOT LONG abierto: {cand_sym} ({qty} @ ${actual_ep:.4f} = ${actual_cost})")
                        break
                    else:
                        print(f"  ⚠️ Spot BUY rechazado en {cand_sym}: {buy_res}")
                        continue

            # 3. Legacy MTF Fallback Path (si algún caller externo envía candidatos sin quant_edge)
            cand_archetype = adaptive_asset_dna.get_asset_dna_archetype(symbol=cand_sym, price=cand_price)
            mtf_res = multi_timeframe_analyzer.analyze_multi_timeframe_candles(cand_sym)
            tf_align = mtf_res.get("timeframe_alignment", {})
            atr_15m = mtf_res.get("atr_pct_15m", 0.45)
            fii = mtf_res.get("fii_score", 0)
            
            # 4. Cooldown Adaptativo & Protocolo de Re-Enganche Inteligente (Fast Re-Entry):
            # Si la moneda fue cerrada recientemente pero presenta:
            # - Doble Suelo / Divergencia RSI, o
            # - FII Institucional >= 65, o
            # - Ignición Verde 1M con volumen,
            # → El Cooldown se anula tras solo 2 minutos (120s) para capturar el rebote explosivo y cubrir comisiones con creces.
            if cand_sym == last_closed_sym and (now_epoch - last_closed_time) < 14400:
                discount_from_exit_pct = ((last_exit_price - cand_price) / last_exit_price) * 100.0 if (last_exit_price > 0 and cand_price > 0) else 0.0
                time_since_last_exit = now_epoch - last_closed_time
                
                is_fast_reentry_eligible = bool(
                    (mtf_res.get("is_double_bottom") or mtf_res.get("bullish_rsi_divergence") or fii >= 65 or mtf_res.get("is_1m_green_ignition")) and
                    time_since_last_exit >= 120
                )
                
                if is_fast_reentry_eligible:
                    print(f"  ⚡ [RE-ENGANCHE INTELIGENTE #{cand_idx}/{total_cands} {cand_sym}] Setup A+ confirmado tras salida previa ({int(time_since_last_exit)}s). Anulando Cooldown para capturar rebote institucional.")
                elif not (is_ai_top and time_since_last_exit >= 300) and not (discount_from_exit_pct >= 1.50 and time_since_last_exit >= 180):
                    mins_passed = int(time_since_last_exit / 60)
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] En Cooldown 4H ({mins_passed}m transcurridos). Pasando al siguiente finalista...")
                    continue  # Cooldown is temporal, cascading is OK
            
            # Re-evaluate archetype with live 15M ATR
            arch_dna = adaptive_asset_dna.get_asset_dna_archetype(cand_sym, atr_15m, cand_price)
            print(f"🧬 [ADN ACTIVO #{cand_idx}/{total_cands}] {cand_sym} ({cand_score} Pts) -> {arch_dna.get('label')} (ATR={atr_15m:.2f}%, SL={arch_dna.get('initial_sl_pct')}%, MaxT={arch_dna.get('max_stagnation_minutes')}m)")
            
            # 6. Veto ADN Tóxico (WR < 40% en SQLite) o Zombi / Mega-Cap lenta (ATR < 0.35%)
            if arch_dna.get("is_toxic_tier", False):
                _dna_prof = arch_dna.get("dna_profile", {})
                _wr_p = _dna_prof.get("win_rate_pct", 0.0)
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por ADN Tóxico en SQLite (WR {_wr_p:.1f}% < 40% histórico). Preservando capital.")
                continue
            if arch_dna.get("is_low_volatility_zombie", False) or atr_15m < 0.25:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por ATR insuficiente ({atr_15m:.2f}% < 0.25%). Zombie sin movimiento.")
                continue
                
            tf_1m = tf_align.get("1m", "BEARISH")
            tf_2m = tf_align.get("2m", "BEARISH")
            tf_5m = tf_align.get("5m", "BEARISH")
            tf_15m = tf_align.get("15m", "BEARISH")
            tf_1h = tf_align.get("1h", "BEARISH")
            tf_10s = tf_align.get("10s", "BEARISH")
            tf_30s = tf_align.get("30s", "BEARISH")
            
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
                mtf_res.get("is_double_bottom") or
                mtf_res.get("bullish_rsi_divergence") or
                mtf_res.get("is_second_touch_sniper") or
                mtf_res.get("is_liquidity_sweep") or
                mtf_res.get("is_sniper_timing_ready") or
                mtf_res.get("is_1m_green_ignition") or
                mtf_res.get("is_yellow_arrow_pivot") or
                mtf_res.get("is_vwap_floor_rebound") or
                mtf_res.get("is_ema_golden_cross") or
                has_dual_sub_minute_ignition
            )
            
            is_active_falling_knife = bool(
                (tf_10s == "BEARISH" and tf_30s == "BEARISH" and tf_1m == "BEARISH") and
                not mtf_res.get("is_bullish_divergence") and
                not mtf_res.get("is_double_bottom") and
                not mtf_res.get("bullish_rsi_divergence") and
                not mtf_res.get("is_second_touch_sniper") and
                not mtf_res.get("is_liquidity_sweep") and
                not mtf_res.get("is_vwap_floor_rebound")
            )
            
            is_15m_cascade = mtf_res.get("is_15m_red_cascade", False)
            is_at_daily_ceiling = mtf_res.get("is_at_daily_resistance_ceiling", False)
            
            if is_at_daily_ceiling or is_15m_cascade:
                if is_ai_top and (fii >= 50 or has_floor_turnaround):
                    # Gemini IA ya evaluó techos y cascadas en sus Agentes 2 y 6
                    print(f"  ⚡ [OVERRIDE IA] {cand_sym}: Techo/Cascada detectada PERO Gemini aprobó (FII={fii}). Permitiendo entrada.")
                else:
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Techo Diario o Cascada 15M.")
                    continue
            # Falling knife: excepción si está en suelo fractal profundo con flujo institucional
            if is_active_falling_knife:
                _range_15m = mtf_res.get("range_position_15m", 0.50)
                if _range_15m <= 0.20 and fii >= 60:
                    print(f"  ⚡ [FALLING KNIFE → SUELO FRACTAL] {cand_sym}: Canal 15M={_range_15m*100:.0f}% FII={fii}. Caída ES el suelo — comprando el rebote.")
                elif is_ai_top:
                    print(f"  ⚡ [FALLING KNIFE → IA APRUEBA] {cand_sym}: Gemini validó giro. Permitiendo entrada.")
                else:
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Cuchillo Cayendo sin suelo fractal.")
                    continue
                
            # 🛑 VETO TOTAL OBV: Si el smart money está distribuyendo, CERO ENTRADAS.
            # Datos empíricos: 100% de victorias en real tienen OBV ACCUMULATING; DISTRIBUTING causó pérdidas
            if mtf_res.get("obv_trend") == "DISTRIBUTING":
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] VETO TOTAL OBV: Distribución en curso (Smart Money vendiendo). Prohibido comprar.")
                continue

            # 🧬 PARÁMETROS ADAPTATIVOS POR ADN Y DICTAMEN IA (Soberanía Gemini AI):
            # Si Gemini AI aprobó el candidato (is_ai_top=True), los umbrales se adaptan dinámicamente
            # a su arquetipo fenotípico y perfil de SQLite en vez de aplicar un bloqueo rígido arbitrario.
            dna_tier = arch_dna.get("dna_tier", "BALANCED")
            is_dna_elite = (dna_tier == "🌟 ÉLITE" or arch_dna.get("archetype") in ["BLUE_CHIP_CORE", "SECTOR_ROTATION"])

            # 💎 VETO 2: FII INSTITUCIONAL — Adaptativo según Soberanía IA y Arquetipo
            if is_ai_top:
                # Si Gemini AI aprobó el setup (Comité 7 Agentes con >=80% de confianza):
                # Memes / High-Beta y activos con giro de suelo fractal tienen inyecciones de FII 35-50.
                if arch_dna.get("archetype") in ["HYPER_VOLATILE_SPRINT", "THIN_BOOK_MICRO"] or has_floor_turnaround:
                    min_fii_req = 35
                else:
                    min_fii_req = 45  # Sincronizado con pipeline_processor (FII >= 45)
            elif is_dna_elite:
                min_fii_req = 55
            else:
                min_fii_req = 60
            if fii < min_fii_req:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] VETO: FII={fii} < {min_fii_req}. Flujo institucional insuficiente.")
                continue

            # 💎 VETO 3: SCORE MÍNIMO — Solo A+ élite
            min_score_req = 80 if is_ai_top else 88
            if cand_score < min_score_req:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] VETO: Score={cand_score} < {min_score_req}. Solo candidatos élite autorizados.")
                continue

            # 💎 VETO 4: VOLUMEN ACTIVO — Impulso real obligatorio (Piso seguro >= 0.65x)
            vol_1m_check = mtf_res.get("vol_surge_1m", 1.0)
            vol_15m_check = mtf_res.get("vol_surge_15m", 1.0)
            min_vol_1m = 0.65 if (is_ai_top and fii >= 70) else 0.70
            min_vol_15m = 0.50

            if vol_1m_check < min_vol_1m:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] VETO VOLUMEN: Vol 1M={vol_1m_check:.2f}x < {min_vol_1m:.2f}x. Sin impulso real suficiente.")
                continue
            if vol_15m_check < min_vol_15m:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] VETO VOLUMEN 15M: Vol 15M={vol_15m_check:.2f}x < {min_vol_15m:.2f}x. Sin liquidez macro suficiente.")
                continue
            elif is_ai_top:
                print(f"  ⚡ [ADN ADAPTATIVO: VOLUMEN APROBADO] {cand_sym} Vol 1M={vol_1m_check:.2f}x >= {min_vol_1m:.2f}x para {arch_dna.get('label')} (FII={fii} | IA Aprobado).")
                
            range_pos_1h = mtf_res.get("range_position_1h", 0.50)
            range_pos_2h = mtf_res.get("range_position_2h", 0.50)
            range_pos_4h = mtf_res.get("range_position_4h", 0.50)
            range_pos_1d = mtf_res.get("range_position_1d", 0.50)
            vol_1m_now = mtf_res.get("vol_surge_1m", 1.0)
            vol_15m_now = mtf_res.get("vol_surge_15m", 1.0)
            rsi_15m_now = mtf_res.get("rsi_15m", 50.0)
            rsi_1m_now = mtf_res.get("rsi_1m", 50.0)
            
            # 🎯 MATRIZ ARMÓNICA MACRO ANTI-TECHO (PROTECCIÓN DE CAPITAL INSTITUCIONAL):
            dist_24h_high = mtf_res.get("dist_to_24h_high_pct", 99.0)
            
            # Umbrales adaptativos sincronizados con pipeline_processor y soberanía IA
            if is_ai_top:
                _max_macro_1d = 0.85
                _max_macro_4h = 0.68
                _max_macro_2h = 0.68
                _max_macro_1h = 0.68
                _max_rsi_15m = 68.0
                _max_rsi_1m = 82.0
                is_near_pump_peak = bool(dist_24h_high < 2.5 and range_pos_4h > 0.70)
            else:
                _max_macro_1d = 0.80
                _max_macro_4h = 0.68
                _max_macro_2h = 0.68
                _max_macro_1h = 0.60
                _max_rsi_15m = 68.0
                _max_rsi_1m = 80.0
                is_near_pump_peak = bool(dist_24h_high < 2.5 and range_pos_4h > 0.70)

            is_macro_base_valid = bool(
                range_pos_1d <= _max_macro_1d and
                range_pos_4h <= _max_macro_4h and
                range_pos_2h <= _max_macro_2h and
                range_pos_1h <= _max_macro_1h and
                rsi_15m_now <= _max_rsi_15m and
                rsi_1m_now <= _max_rsi_1m and
                not is_near_pump_peak
            )
            
            _ceiling_veto = is_at_daily_ceiling and not is_ai_top
            if not is_macro_base_valid or _ceiling_veto:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado: En Techo Macro o Sobrecomprado:")
                print(f"     Canales Macro: [1H: {range_pos_1h*100:.0f}% (max {_max_macro_1h*100:.0f}) | 2H: {range_pos_2h*100:.0f}% (max {_max_macro_2h*100:.0f}) | 4H: {range_pos_4h*100:.0f}% (max {_max_macro_4h*100:.0f}) | 1D: {range_pos_1d*100:.0f}% (max {_max_macro_1d*100:.0f}) | RSI15M: {rsi_15m_now:.1f} (max {_max_rsi_15m:.0f})]")
                continue

            if is_ai_top:
                has_floor_turnaround = True  # El Comité IA ya validó el giro y suelo de mercado

            if not has_floor_turnaround:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Falta de Giro de Suelo en 1M/2M.")
                continue

            # ═══════════════════════════════════════════════════════════════════
            # 🛡️ FILTRO ANTI-RENDER: FII mínimo aumentado cuando RSI 15M > 45
            # RENDER entró con FII=60 + RSI15m=43 — no es suficiente confirmación institucional
            # para un activo en zona de consolidación bajista. Exigir FII >= 65.
            # ═══════════════════════════════════════════════════════════════════
            rsi_15m_val = mtf_res.get("rsi_15m", 50.0)
            if rsi_15m_val >= 45.0 and fii < 65 and not is_ai_top:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por FII Insuficiente con RSI 15M neutral (RSI15M={rsi_15m_val:.1f} >= 45 pero FII={fii} < 65). Exige FII >= 65 para zona no-oversold.")
                continue

            # ═══════════════════════════════════════════════════════════════════
            # 🛡️ FILTRO ANTI-RENDER: Momentum 5M bajista activo
            # Si los últimas 5 velas de 5M tienen >= 3 rojas con mayor volumen en rojas
            # que en verdes → distribución activa → entrada prohibida aunque la 8D diga base.
            is_spring = mtf_res.get("spring_coiling", {}).get("is_spring_compressed", False)
            is_wave2 = mtf_res.get("wave2_retest", {}).get("is_wave2_retest", False)

            # ═══════════════════════════════════════════════════════════════════
            try:
                import api_connector as _self
                kl_5m = _self.get_klines(cand_sym, "5m", 5)
                if kl_5m and len(kl_5m) >= 4:
                    reds = [(float(k[2]) - float(k[3])) for k in kl_5m if float(k[4]) < float(k[1])]
                    greens = [(float(k[2]) - float(k[3])) for k in kl_5m if float(k[4]) >= float(k[1])]
                    red_vol = sum(float(k[5]) * float(k[4]) for k in kl_5m if float(k[4]) < float(k[1]))
                    green_vol = sum(float(k[5]) * float(k[4]) for k in kl_5m if float(k[4]) >= float(k[1]))
                    red_count = len([k for k in kl_5m if float(k[4]) < float(k[1])])
                    # Block if: 3+ red candles AND red volume dominates (>= 62% of total volume)
                    total_vol_5m = red_vol + green_vol
                    red_vol_pct = (red_vol / total_vol_5m * 100) if total_vol_5m > 0 else 50.0
                    if red_count >= 3 and red_vol_pct >= 62.0 and not (fii >= 65 or is_spring or is_ai_top):
                        print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Momentum 5M Bajista Activo ({red_count}/5 velas rojas | VolRojo={red_vol_pct:.0f}% del flujo). Distribución activa — esperar reversión real.")
                        continue
            except Exception:
                pass


            if (mtf_res.get("rsi_2m", 50.0) > 65.0 or mtf_res.get("rsi_1m", 50.0) > 65.0) and not (is_spring or is_wave2):
                # Si la IA aprobó el activo (is_ai_top) o hay ignición/giro confirmado, permitir RSI hasta 78.0 en timeframe corto
                if is_ai_top or has_floor_turnaround:
                    rsi_hard_cap = 78.0
                elif vol_1m_now >= 1.2 or fii >= 45 or has_dual_sub_minute_ignition:
                    rsi_hard_cap = 72.0
                else:
                    rsi_hard_cap = 68.0
                if mtf_res.get("rsi_2m", 50.0) > rsi_hard_cap or mtf_res.get("rsi_1m", 50.0) > rsi_hard_cap:
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Entrada Tardía (RSI 2M={mtf_res.get('rsi_2m'):.1f} > {rsi_hard_cap:.0f}).")
                    continue

            # 🔄 CONFIRMACIÓN DE REBOTE: No comprar EN el suelo mientras cae, comprar cuando YA REBOTÓ
            # La última vela de 1M debe ser VERDE, o ascendente, o tener mecha de absorción inferior >= 38%
            try:
                _kl_bounce = get_klines(cand_sym, "1m", 3)
                if _kl_bounce and len(_kl_bounce) >= 2:
                    _last_open = float(_kl_bounce[-1][1])
                    _last_high = float(_kl_bounce[-1][2])
                    _last_low = float(_kl_bounce[-1][3])
                    _last_close = float(_kl_bounce[-1][4])
                    _prev_close = float(_kl_bounce[-2][4])
                    _is_green = _last_close > _last_open
                    _is_rising = _last_close > _prev_close
                    _c_range = _last_high - _last_low
                    _lower_wick = min(_last_open, _last_close) - _last_low
                    _has_wick_abs = (_lower_wick / _c_range >= 0.38) if _c_range > 0 else False
                    
                    if not _is_green and not _is_rising and not _has_wick_abs:
                        print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Sin confirmación de rebote (última vela 1M roja y descendente sin absorción). Esperando rebote real en el suelo.")
                        continue
                    elif _has_wick_abs and not _is_green:
                        print(f"  🕯️ [ABSORCIÓN EN PISO] {cand_sym}: Mecha inferior de rechazo ({_lower_wick/_c_range*100:.0f}%). Compradores absorbiendo soporte.")
            except Exception:
                pass
                
            # 7. Orderbook Depth & Micro-Surge Checks
            ob_info = orderbook_analyzer.fetch_orderbook_depth(cand_sym, limit=20)
            spread_now = ob_info.get("spread_pct", 0.0)
            bid_dom_now = ob_info.get("bid_dominance_pct", 50.0)
            
            max_allowed_spread = 0.30 if ob_info.get("bid_vol_usdt", 0.0) >= 25000.0 else 0.28
            if spread_now > max_allowed_spread:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Spread excesivo ({spread_now:.3f}% > {max_allowed_spread:.3f}%).")
                continue
                
            min_bid_dom = 45.0 if is_ai_top else (46.0 if (fii >= 46 and ob_info.get("bid_vol_usdt", 0.0) >= 15000.0) else 48.0)
            if bid_dom_now < min_bid_dom:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Bids insuficientes ({bid_dom_now:.1f}% < {min_bid_dom:.1f}%).")
                continue
                
            # 🎯 CANDADO FRANCOTIRADOR: Profundidad mínima de libro institucional
            # Prohíbe entrar en tokens con libros delgados donde una venta retail cause un slippage severo.
            _min_bids_usd = 12000.0 if is_ai_top else 20000.0
            if ob_info.get("bid_vol_usdt", 0.0) < _min_bids_usd:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Muro Bids delgado (${ob_info.get('bid_vol_usdt', 0.0):,.0f} < ${_min_bids_usd:,.0f}). Exige liquidez institucional pesada.")
                continue
                
            vol_1m_now = mtf_res.get("vol_surge_1m", 1.0)
            vol_2m_now = mtf_res.get("vol_surge_2m", 1.0)
            vol_15m_now = mtf_res.get("vol_surge_15m", 1.0)
            is_30s_burst = mtf_res.get("is_30s_micro_burst", False)
            vol_acc = mtf_res.get("vol_acceleration", 1.0)
            is_pre_pump = mtf_res.get("is_pre_pump_signal", False)
            tf_1m_up = mtf_res.get("tf_1m_up", False)
            is_1m_wick = mtf_res.get("is_1m_lower_wick_absorption", False)
            
            # 🚀 REGLA DE LIQUIDEZ Y VOLUMEN ACTIVO (Permite compresión natural en soporte con FII >= 50):
            if vol_15m_now < 0.10 and vol_1m_now < 0.20:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Volumen Abandonado ({vol_1m_now:.2f}x 1M / {vol_15m_now:.2f}x 15M).")
                continue
                
            # BUG FIX: ATOM slipped through with vol_surge=0.02 because FII>=50 bypassed. 
            # Now vol_surge_1m >= 0.20 is MANDATORY regardless of FII. FII only upgrades ignition, not replaces it.
            if vol_1m_now < 0.20:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Volumen 1M muerto ({vol_1m_now:.2f}x < 0.20x). Mínimo de actividad de compradores obligatorio.")
                continue

            # ═══════════════════════════════════════════════════════════════════════
            # 🎯 CLASIFICADOR MODO SNIPER vs ESTÁNDAR
            # Para lograr +1% diario neto REAL, necesitamos distinguir entre:
            #   SNIPER (explosivo): vol_surge >= 1.5x + FII >= 70 + RSI15M < 38
            #     → Target: +1.2%+ ganancia. Retener más tiempo. No micro-scratch.
            #   ESTÁNDAR (normal): Cumple filtros base pero no tiene toda la potencia
            #     → Reglas normales. Target: +0.43% promedio.
            # La diferencia: un SNIPER aporta +1.2% de ganancia, vs +0.43% estándar.
            # Con solo 1-2 snipers por día ya superamos el 1% neto libre de comisiones.
            # ═══════════════════════════════════════════════════════════════════════
            rsi_15m_check = mtf_res.get("rsi_15m", 50.0)
            atr_15m_check = mtf_res.get("atr_pct_15m", 0.0)
            is_sniper_setup = bool(
                vol_1m_now >= 1.5 and          # Volumen explosivo real (no suave)
                fii >= 70 and                   # Institucionales activamente comprando
                rsi_15m_check <= 38.0 and       # Oversold real — no zona neutral
                atr_15m_check >= 0.50           # Rango suficiente para alcanzar +1.2%+
            )
            is_super_sniper = bool(
                is_sniper_setup and
                vol_1m_now >= 2.5 and           # Volumen ultra-explosivo
                fii >= 80 and                   # Confirmación institucional fuerte
                rsi_15m_check <= 32.0           # Oversold extremo — rebote casi garantizado
            )

            if is_super_sniper:
                print(f"  ⚡ [SÚPER SNIPER] {cand_sym}: Vol={vol_1m_now:.1f}x FII={fii} RSI15M={rsi_15m_check:.0f} ATR={atr_15m_check:.2f}% — TARGET: +1.5%+ GARANTIZADO")
            elif is_sniper_setup:
                print(f"  🎯 [MODO SNIPER] {cand_sym}: Vol={vol_1m_now:.1f}x FII={fii} RSI15M={rsi_15m_check:.0f} ATR={atr_15m_check:.2f}% — TARGET: +1.2%+")
            else:
                print(f"  📊 [ESTÁNDAR] {cand_sym}: Vol={vol_1m_now:.1f}x FII={fii} RSI15M={rsi_15m_check:.0f} — Target: +0.43% normal")

            # 🎯 MODO FRANCOTIRADOR PURO (CUENTA REAL):
            # Cero tolerancia a setups estándar tibios en libros delgados.
            # Solo se dispara si cumple confluencia pesada de Francotirador:
            # 1. Soberanía Gemini AI (is_ai_top == True y Muro Bids >= $12k), O
            # 2. is_sniper_setup == True, O
            # 3. Confluencia Élite Pesada: FII >= 55 + Muro Bids >= $12k + Score >= 85 + VolSurge 15M >= 0.35x
            is_elite_francotirador = bool(
                is_sniper_setup or
                (is_ai_top and ob_info.get("bid_vol_usdt", 0.0) >= 12000.0) or
                (fii >= 55 and ob_info.get("bid_vol_usdt", 0.0) >= 12000.0 and cand_score >= 85 and vol_15m_now >= 0.35)
            )
            if not is_elite_francotirador:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por MODO FRANCOTIRADOR: Setup sin confluencia pesada (FII={fii}, Muro Bids=${ob_info.get('bid_vol_usdt', 0.0):,.0f}, Vol15M={vol_15m_now:.2f}x). Solo tiros A+ autorizados para dinero real.")
                continue

            is_dead_volume = (vol_1m_now < 0.20 or vol_15m_now < 0.12)
            has_active_ignition = (
                (vol_1m_now >= 0.50 and vol_15m_now >= 0.15) or 
                (vol_2m_now >= 0.50 and vol_15m_now >= 0.15) or 
                (vol_15m_now >= 0.50) or 
                (vol_1m_now >= 0.80) or
                (vol_acc >= 1.10 and vol_15m_now >= 0.15) or
                (fii >= 60 and vol_1m_now >= 0.20) or
                (is_ai_top and vol_1m_now >= 0.20) or  # Soberanía IA en base fractal
                is_spring or
                is_wave2 or
                is_cetus_rocket or
                is_pre_pump or
                is_30s_burst
            )
            tf_2m_up = mtf_res.get("tf_2m_up", False)
            tf_5m_up = mtf_res.get("tf_5m_up", False)
            has_trigger_candle = (
                tf_1m_up or 
                is_1m_wick or 
                tf_2m_up or
                (fii >= 55 and tf_5m_up) or
                mtf_res.get("is_ground_zero_micro_ignition", False) or
                (is_ai_top and has_floor_turnaround)
            )
            
            if is_dead_volume or not has_active_ignition:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Volumen Muerto/Sin Ignición Real (1M={vol_1m_now:.2f}x, 15M={vol_15m_now:.2f}x). Exige compradores activos.")
                continue
                
            if not has_trigger_candle:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Descartado por Vela 1M Roja en caída sin mecha de absorción. Exige giro verde.")
                continue
                
            final_cand_score = max(cand_score, mtf_res.get("multi_tf_score", 50))
            req_min_score = min(70, min_required_score) if is_ai_top else min_required_score
            if final_cand_score < req_min_score:
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] Score insuficiente ({final_cand_score} < {req_min_score}).")
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
                _cci_display = f"{cci_val:.0f}" if cci_val is not None else "N/A"  # BUG 2 FIX: guard None
                print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] CCI Sobrecomprado ({_cci_display} >= 150). Entrada prohibida en cima.")
                continue
            
            # 🧬 BLACKLIST DINÁMICA TIERED + WHITELIST ÉLITE (Aprendizaje de Simulaciones + Cuenta Real):
            token_dna_label = ""
            try:
                import learning_engine
                # Load blacklist and elite once per candidate evaluation cycle (cached)
                _dyn_bl = learning_engine.get_dynamic_blacklist()
                _dyn_elite = learning_engine.get_dynamic_elite()
                
                bl_entry = _dyn_bl.get(cand_sym)
                if bl_entry:
                    tier = bl_entry["tier"]
                    tier_label = {"HARD": "☠️ TÓXICO HARD", "MID": "🔴 TÓXICO MID", "SOFT": "🟠 TÓXICO SOFT"}.get(tier, "⛔ TÓXICO")
                    print(f"  ⛔ [#{cand_idx}/{total_cands} {cand_sym}] ADN {tier_label}: WR={bl_entry['win_rate']:.0f}% en {bl_entry['total_trades']} trades (PnL acum: ${bl_entry['pnl_usd']:.2f}). Blacklist dinámica activa.")
                    continue
                
                elite_entry = _dyn_elite.get(cand_sym)
                if elite_entry:
                    token_dna_label = f" | 🌟 ADN ÉLITE ({elite_entry['win_rate']:.0f}% WR en {elite_entry['total_trades']} ops | +${elite_entry['pnl_usd']:.2f})"
                    # Boost score for elite tokens
                    final_cand_score = min(100, final_cand_score + 10)
                else:
                    # Standard DNA label from profile
                    token_profile = learning_engine.get_token_dna_profile(cand_sym)
                    token_wr = token_profile.get("win_rate", 50.0)
                    token_trades = token_profile.get("total_trades", 0)
                    if token_trades >= 3:
                        streak = token_profile.get("streak", "NEUTRAL")
                        streak_icon = "🔥" if streak == "HOT_STREAK" else ("❄️" if streak == "COLD_STREAK" else "📊")
                        token_dna_label = f" | {streak_icon} ADN ({token_wr:.0f}% WR en {token_trades} ops)"
            except Exception:
                pass
            
            # ═════════════════════════════════════════════════════════════════════════
            # 💎 TARJETA EJECUTIVA CUÁNTICA UNIFICADA (DICTAMEN IA + EJECUCIÓN SPOT)
            # ═════════════════════════════════════════════════════════════════════════
            trend_label = "📈 TENDENCIA FUERTE" if is_bullish_adx else ("📊 RANGO" if is_ranging else "📈 NEUTRAL")
            cci_label = f"CCI={cci_val:.0f}" if cci_val is not None else "CCI=N/A"
            adx_label = f"ADX={adx_val:.0f}" if adx_val is not None else "ADX=N/A"
            
            # Fix: extraer variables de canal micro que no se definían en este scope
            range_pos_1m  = mtf_res.get("range_position_1m",  0.50)
            range_pos_2m  = mtf_res.get("range_position_2m",  0.50)
            range_pos_5m  = mtf_res.get("range_position_5m",  0.50)
            range_pos_10m = mtf_res.get("range_position_10m", 0.50)
            range_pos_15m = mtf_res.get("range_position_15m", 0.50)
            range_pos_30m = mtf_res.get("range_position_30m", 0.50)

            print(f"\n💎 ═══════════════════════════════════════════════════════════════════════════════════")
            print(f"🚀 [DICTAMEN & EJECUCIÓN CUÁNTICA SPOT: #{cand_idx}/{total_cands} -> {cand_sym}]")
            print(f"═══════════════════════════════════════════════════════════════════════════════════════")
            print(f"🧬 Arquetipo ADN: {cand_archetype.get('label')} | SL Inicial: {arch_dna.get('initial_sl_pct', -2.00)}% | Cosecha Fase 2: +0.44%{token_dna_label}")
            print(f"📊 Score MTF: {final_cand_score}/100 | FII Suelo: {fii}/100 | ATR: {atr_15m:.2f}% | Spread: {ob_info.get('spread_pct'):.3f}%")
            print(f"🌌 Canales Fractales: [1M: {range_pos_1m*100:.0f}% | 2M: {range_pos_2m*100:.0f}% | 5M: {range_pos_5m*100:.0f}% | 10M: {range_pos_10m*100:.0f}% | 15M: {range_pos_15m*100:.0f}% | 30M: {range_pos_30m*100:.0f}% | 1H: {range_pos_1h*100:.0f}% | 2H: {range_pos_2h*100:.0f}%]")
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
                
            print(f"🔬 [PRE-BUY CHECK] Verificando micro-flujo Volume Delta para {cand_sym} (${usdt_free:.2f} USDT)...")

            # ═══════════════════════════════════════════════════════════════════════
            # ⚡ VOLUME DELTA PRECISION GATE — Sub-Second Entry Timing
            # Checks aggressive Taker Buy vs Taker Sell flow in the last 30 seconds.
            # Like the green/red bar indicator on TradingView — it anticipates moves 1-5s early.
            # ═══════════════════════════════════════════════════════════════════════
            try:
                import volume_delta_engine
                vd = volume_delta_engine.get_volume_delta_signal(cand_sym, window_seconds=30)
                vd_buy = vd.get("buy_ratio_pct", 50.0)
                vd_sell_wave = vd.get("sell_wave", False)
                vd_entry_ok = vd.get("entry_approved", True)
                vd_label = vd.get("signal_label", "Sin datos")
                vd_delta = vd.get("delta_usdt", 0.0)
                vd_accel = vd.get("delta_acceleration", 0.0)
                print(f"⚡ [VOLUME DELTA] {cand_sym}: {vd_label}")

                # BUG 2 FIX: Eliminar excepción FII≥70 para buy ratio.
                # Con BTC bajista, FII alto NO compensa flujo vendedor en la pantalla.
                # Los institucionales compran OTC pero los retails venden en mercado = caída de precio.
                # Regla unificada: si vemos más vendedores que compradores → VETO sin importar FII.
                # Mercado normal: buy≥45% | Con BTC bajista: buy≥48% (más estricto)
                # ⚡ REGLA INVIOLABLE DE VOLUMEN DELTA: Solo entrar cuando los COMPRADORES tienen el control activo.
                # Auditoría de 68 operaciones reveló que permitir vd_min_buy=38% causó el 87% de las pérdidas históricas.
                # NUNCA comprar cuando los vendedores de mercado superan a los compradores.
                _is_btc_bearish_now = is_bearish  # 'is_bearish' se pasa desde pipeline
                vd_min_buy = 52.0 if not _is_btc_bearish_now else 54.0
                if vd_sell_wave or vd_buy < vd_min_buy or vd_accel <= -5.0:
                    print(f"  🛑 [VOLUME DELTA VETO] {cand_sym} descartado: Dominancia vendedora taker activa (Buy={vd_buy:.0f}% < {vd_min_buy:.0f}%, Accel={vd_accel:+.1f}%, FII={fii}, BTC_bajista={_is_btc_bearish_now}, Delta={vd_delta:+,.0f} USDT). Esperando compradores agresivos.")
                    continue

                # BOOST: Strong buy delta unlocks entry even at moderate score
                if vd.get("strong_buy", False) or vd_buy >= 55.0:
                    print(f"  🚀 [VOLUME DELTA BOOST] Flujo comprador agresivo confirmado (Buy={vd_buy:.0f}%). Entrada de máxima precisión.")
            except Exception as _vde:
                print(f"  ⚠️ [VOLUME DELTA] Sin datos de flujo ({_vde}). Continuando con filtros estándar.")

            # ═══════════════════════════════════════════════════════════════════════
            # 🛡️ BUG 5 FIX: PRE-BUY FINAL GATE — Chequeo OBV + BTC justo antes de comprar
            # El pipeline puede aprobar un candidato, pero entre el escaneo (~30s antes)
            # y la ejecución real las condiciones pueden haber cambiado.
            # Si BTC bajista Y el OBV del activo es DISTRIBUTING → CANCELAR compra.
            # ═══════════════════════════════════════════════════════════════════════
            try:
                _pre_buy_obv = mtf_res.get("obv_trend", "NEUTRAL")
                if _pre_buy_obv == "DISTRIBUTING":
                    print(f"  🔴 [PRE-BUY GATE] {cand_sym} CANCELADO: OBV=DISTRIBUTING al momento de ejecutar (dinero institucional vendiendo). Capital protegido.")
                    continue
                # También verificar que BTC no haya caído un 0.5% adicional desde el escaneo inicial
                try:
                    _btc_now_px = get_symbol_price("BTCUSDT", is_futures=False)
                    _btc_entry_px = cand_info.get("btc_ref_price", _btc_now_px)
                    if _btc_entry_px and _btc_now_px:
                        _btc_drop_since_scan = (_btc_now_px - _btc_entry_px) / _btc_entry_px * 100
                        if _btc_drop_since_scan < -0.5:
                            print(f"  🔴 [PRE-BUY GATE] {cand_sym} CANCELADO: BTC cayó {_btc_drop_since_scan:.2f}% desde el escaneo. Condiciones deterioradas.")
                            continue
                except Exception:
                    pass  # No bloquear si no hay datos comparativos

                # 🛡️ CENTINELA DE MICRO-CAÍDA BTC (1M): Jamás disparar una compra si Bitcoin está cayendo activamente en 1M
                try:
                    _btc_1m = get_klines("BTCUSDT", "1m", 2)
                    if _btc_1m and len(_btc_1m) >= 1:
                        _b1_o = float(_btc_1m[-1][1])
                        _b1_c = float(_btc_1m[-1][4])
                        _b1_ret = ((_b1_c - _b1_o) / _b1_o * 100.0) if _b1_o > 0 else 0.0
                        if _b1_ret < -0.35:
                            print(f"  🛑 [PRE-BUY GATE] {cand_sym} CANCELADO: Bitcoin en caída rápida 1M ({_b1_ret:+.2f}%). Protegiendo capital hasta estabilización.")
                            continue
                except Exception:
                    pass
            except Exception as _pb_err:
                print(f"  ⚠️ [PRE-BUY GATE] Error en chequeo final ({_pb_err}). Continuando.")

            print(f"🚀 [ORDEN A MERCADO SPOT] Enviando orden de compra en {cand_sym} con ${usdt_free:.2f} USDT (100% Capital)...")
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
                    "pump_probability_pct": mtf_res.get("predictive_dna", {}).get("pump_probability_pct", 50),
                    "btc_entry_price": get_symbol_price("BTCUSDT", is_futures=False) or 0.0,
                    "is_sniper_setup": is_sniper_setup,
                    "is_super_sniper": is_super_sniper,
                }
                state["status"] = f"🔵 En Vivo LONG ({cand_sym} @ ${actual_entry_price:.4f})"
                state["_cached_usdt_free"] = 0.0
                save_real_account_state(state)
                print(f"✅ SPOT LONG ejecutado exitosamente: {cand_sym} ({qty} @ ${actual_entry_price:.4f} = ${actual_cost} USD)")
                # Marcar que ya se ejecutó 1 trade en este ciclo — bloquea candidatos adicionales
                _trade_executed_this_cycle = True
                try:
                    import asset_dna_predictive_engine as _adna
                    _adna.register_trade_today(cand_sym)
                except Exception:
                    pass
                executed_trade = True
                break
                
        if not executed_trade:
            print(f"🔒 [CASCADE EVALUATION TOP 100 CMC] Se evaluaron los {len(candidate_queue)} candidatos con ADN Activo y Confluencia 8D. Ninguno superó el 100% de los filtros en este ciclo. 100% USDT protegido.")

    state["current_balance_usd"] = round(state.get("current_balance_usd", 20.07), 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - state.get("initial_deposit_usdt", 17.13), 2)
    if executed_trade:
        state["last_trade_time"] = now_str
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
