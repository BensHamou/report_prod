from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.utils.html import format_html
from account.models import Line
from report.models import Report
def send_alert():
    
    # get all lines that have include_cron = True
    lines = Line.objects.filter(include_cron=True)
    current_time = datetime.now()
    today = datetime.today().date()

    for line in lines:
        for shift in line.shifts():
            shift_end_time = time(shift.hour_end, shift.minutes_end)
            allowed_delay = timedelta(minutes=line.allowed_delay)
            threshold = datetime.combine(datetime.today(), shift_end_time) + allowed_delay
            threshold_limit = datetime.combine(datetime.today(), shift_end_time) + allowed_delay + timedelta(minutes=120)

            if threshold <= current_time <= threshold_limit:
                alert = True
                if shift.hour_start > shift.hour_end:
                    yesterday = datetime.now() - timedelta(days=1)
                    latest_report = Report.objects.filter(line=line, shift=shift, prod_day=yesterday.strftime('%Y-%m-%d')).first()
                else:
                    latest_report = Report.objects.filter(line=line, shift=shift, prod_day=today).first()
                
                if latest_report:
                    alert = False
                
                recipient_list = []
                
                if line.site.address:
                    recipient_list = line.site.address.split('&')
                else:
                    recipient_list = ['benshamou@gmail.com']
                #recipient_list = ['benshamou@gmail.com']
                #recipient_list = ['senoucisan@gmail.com']

                subject = 'Notification d\'alerte ' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                message = '''<p>Le rapport du shift [''' + shift.__str__() + '''] du ligne '''+line.__str__()+'''<b> n'est pas encore créé.</b>'''

                formatHtml = format_html(message)
                if alert:
                    #print('HERE', line, shift)
                    send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)