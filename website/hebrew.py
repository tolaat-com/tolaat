import re

website_name = 'תולעת המשפט'
website_description='מאגר משפטי חכם, פתוח, ידידותי והכי מתקדם טכנולוגית'
case = 'תיק'
transport_case = 'תיק-תעבורה'
supreme_case = 'תיק-עליון'
all_cases_url = 'כל-התיקים'
judge = 'שופט/ת'
court = 'בית משפט'
status = 'מצב'
reason_status = 'סיבת סגירה'
verdictResultName = 'תוצאה'
dateOpen = 'תאריך פתיחה'
dateClose = 'תאריך סגירה'

view='צפיה'
view_document='צפיה-במסמך'
document='מסמך'
download='הורדה'

n_cases = '({} תיקים)'
one_case = '(תיק אחד)'

og_description_case = 'ב{} בפני {}'


linked_cases = 'תיקים קשורים'
   
linked_case_status = 'מצב' 
linked_case_sug = 'סוג'
linked_case_inian = 'עניין'
linked_case_court = 'בית משפט'
linked_case_name = 'שם'
linked_case_number = 'מספר'
linked_case_relation = 'קשר'

parties = 'צדדים'
party_role = 'תפקיד'
party_name = 'שם'
party_repr = 'בא/י כח'
claimAmount='סכום התביעה'
actionSum='סכום תביעה יצוגית'
inian='עניין'
sug='סוג תיק'
proceedingName = 'סוג הליך'
caseTypeDesc='פירוט נוסף'
no_decisions = 'לא נמצאו החלטות בתיק זה'
decisions = 'החלטות'
decision = 'החלטה'
decision_sug = 'סוג'
decision_date = 'תאריך'
decision_signer = 'גורם חותם'
decision_type = 'סוג מסמך'
decision_name = 'נושא'
decision_pages = 'עמודים'
document = 'מסמך'
verdicts='פסקי דין'
verdict_url='פסק-דין'
preview_name = 'תצוגה-ישירה'
preview_decision='החלטה'
preview_verdict='פסק דין'
preview_original='מקור'
preview_scrapped_just_now='הועתק מהשרת הממשלתי ממש עכשיו'

scrap_request='בקשת-גירוד'
scrap_form ='טופס-גירוד'
scrap_form_submit='הגשת-טופס-גירוד'


sittings = 'ישיבות'
sitting_status = 'מצב'
sitting_who = 'גורם'
sitting_bakasha ='בקשה'
sitting_canceled = 'בוטל'
sitting_time = 'מועד'

sitting3_type = 'סוג'
sitting3_endtime = 'סיום'
sitting3_has_protocol = 'פרוטוקול'
sitting3_date = 'תאריך'
sitting3_status = 'מצב'
sitting3_start = 'התחלה'
sitting3_user = 'גורם'

results_pages = 'עמוד תוצאות {} מתוך {}'

page = 'דף'

confidential = 'תיק חסוי'
yes = 'כן'

lawyer = "עו\"ד"
side_old = "בעל/ת-דין"
side = "צד-להליך"
represented = "עוה\"ד {} ייצג/ה ב-{} תיק/ים"

ugc='תוכן גולשים'
import os
if os.environ.get('netanyahu') == 'true':
    ugc_url = 'מסמכים-נוספים'
else:
    ugc_url='תוכן-גולשים'
ugc_form = 'טופס-מסמכים'
ugc_submit='קידוד-מסמך'
ugc_beta ='תוכן גולשים (בהרצה)'
ugc_beta_message='מסמכים שנשלחו לתולעת המשפט על ידי צדדים או בעלי עניין בהליך (בהרצה).'
ugc_date ='תאריך העלאה'
ugc_title = 'כותרת'
ugc_pages = 'עמודים'
ugc_disclaimer='תולעת המשפט מוותרת על כל טענת זכות בקשר לתוכן גולשים. ייתכן כי לצדדים אחרים, כגון בעלי דין ועורכי דין הם בעלי זכויות קניין ואחרות'

netanyahu_ugc = 'מסמכים נוספים מנט המשפט'

fax_max_pages = 'לא ניתן לשלוח פקס עם יותר מ-4 עמודים'
fax_non_zero_origin = 'עמוד לא מתחיל באפס'
fax_width_gt = 'עמוד עם רוחב {} גדול מהתקין ({})'
fax_width_lt = 'עמוד עם רוחב {} קטן מהתקין ({})'
fax_free='פקס-חינם-לבית-המשפט'
fax_free_title='פקס חינם לבית המשפט'
fax_bad_height = 'עמוד עם אורך לא תקין'
fax_prefix = 'פקס'
fax_form = 'טופס-הכנה'
fax_submit = 'העלאה'
fax_send ='שליחה'
fax_after='אחרי'
fax_send_confirmation ='אישור-שליחה'
fax_agree='עליך להסכים עם תנאי השימוש'

lawyer_subtitle = 'תיקים בהם ייצג/ה עו"ד בשם {}'
side_subtitle = 'תיקים בהם מופיע {} כשם של בעל/ת דין'
judge_subtitle = 'תיקים בהם ישב {}'
pair_subtitle = 'תיקים בהם מופיע צמד עם השמות {}'

entity_subtitle = {
    'J': judge_subtitle,
    'L': lawyer_subtitle,
    'S': side_subtitle,
    'P': pair_subtitle
}
num_of_cases = '{} תיקים'

pairs = 'שחקנים חוזרים'
pair_and = '{} ו{}'
pair_appearance = 'השמות {} ו{} מופיעים ביחד ב-{} תיקים'

party_url = "בעל-דין"
cases_page = " ".join(['תיקים', '{}', 'עד', '{}', 'מתוך', '{}'])

next = "הבא"
previous = "הקודם"
showing_page = 'מציג כעת דף תוצאות {}'
results_from_to = 'תוצאת {} עד {}'
for_search_query = 'עבור שאילתת חיפוש: '
search_result_title='תוצאות חיפוש פסקי דין עבור {}, דף מספר {}'

side_appeared = "{} מופיע/ה כצד להליך ב-{} תיק/ים"
lawyer_appears = "עו\"ד בשם {} מופיע/ה כמייצג/ת ב-{} תיקים"

judge_appears = "{} ישב/ה ב-{} תיק/ים"
side_subtitle = 'תיקים בהם מופיע/ה {} כבעל דין'

judge_url = "שופט-ת"
tik_plili = '(ת\"פ)'
welcome = 'ברוכים הבאים'

unfit = '[נאשם אי כשיר לעמוד לדין]'

total_cases = 'קיימים {} תיקים במאגר'
appears = '{} מופיע/ה ב-{} תיקים'
search = 'חיפוש'
developers = 'מפתחים'
show_search_results = 'הצג תוצאות חיפוש'

ktav_teanot = 'כתב טענות'
kitvei_teanot='כתבי טענות'
kitvei_teanot_name='כתב טענות'
kitvei_teanot_date='תאריך'

document_types_e2h = {
    'decisions': 'החלטה',
    'kitvei_teanot': 'כתב טענות'
}

document_types_h2e = {v: k for k, v in document_types_e2h.items()}


supreme_court_case = 'תיק בית המשפט העליון'
view_official_site = 'צפיה באתר הממשלתי'

short_url = 'כתובת מקוצרת'
privacy = 'פרטיות'
contact = 'צור קשר'
changelog = 'יומן שינויים'
no_censorship = 'אי הסרת מידע'
cases_list = 'רשימת תיקים'

copy = 'העתק'

scraped = 'הועתק מהשרת הממשלתי ב-{}.'
doc_scraped = 'המסמך הועתק מהשרת הממשלתי ב-{}.'
master_scraped = 'החלטות, פסקי דין וישיבות הועתקו מחדש ב-{}.'
recompute = 'ישויות וקשרים חושבו בפעם האחרונה ב-{}.'

failed_capcha = 'בוטים לא עובדים בשביל בוטים.'

generic_views_h2e = {
    case: 'n',
    transport_case: 't',
    supreme_case:  'e'
}

about  = 'אודות'

generic_views_e2h = {}
for k, l in generic_views_h2e.items():
    for v in l:
        generic_views_e2h[v] = k

bodily_harm = ['נזק גוף', 'נזקי גוף', 'פלת"ד' , 'נפגעי עבודה', 'ערעור לפי חוק הנכים']
plaintiff_re = 'תובע' + ' ' + '[0-9]+'
anonimous = 'פלוני'
anonymized = '[חסיון 70 (ג1)]'
censored = '[נאסר לפרסום]'
gag_order = 'צו איסור פרסום'
missing_info = 'קרא עוד על חסיון 70 (ג1)'
bodily_harm_link = 'חיסיון תובע נזקי גוף'
against = "נ'"

hidden_document = 'לא ניתן לצפות במסמך זה. ייתכן שהוא זמין בנט המשפט.'

key='מפתח'
show_key='כן'

feeling_lucky='אני מרגיש בר מזל'

version='גרסת-נתונים'

def urlize(n):
    return re.sub('\\W+', '-', n.strip())

import datetime

months = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']


def ymd(timestamp):
    dt = datetime.date.fromtimestamp(int(timestamp))
    y = dt.year
    m = months[dt.month-1]
    d = dt.day
    be = 'ב'
    return f'{d} {be}{m} {y}'


login='כניסה'
logout='יציאה'

toggle_hide='הסתרה'


decision_types_h2e = {decision: 'decisions', verdict_url: 'verdicts'}
decision_types_e2h = {'decisions': decision, 'verdicts': verdict_url}


email_form = 'טופס-דואר'
email_form_submit = 'שליחת-טופס-דואר'
email_form_submit_authorize = 'הודעת-אישור-דואר'
email_pending = 'טרם לחצת על קישורית האישור'
email_failed = 'הכנס אימייל מחדש לקבלת קישורית אישור'

email_form_title = 'טופס דואר'
email_bad_address ='כתובת לא תקינה'

external='תיק-חיצוני'
external_CaseDisplayIdentifier='מספר'
external_CaseTypeShortName='שם'
external_CaseLinkTypeName='סוג'
external_h2e = {
    external_CaseDisplayIdentifier: 'CaseDisplayIdentifier',
    external_CaseTypeShortName: 'CaseTypeShortName',
    external_CaseLinkTypeName: 'CaseLinkTypeName'
}

external_e2h = {v:k for k,v in external_h2e.items()}