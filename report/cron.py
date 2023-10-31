from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.utils.html import format_html
from account.models import Line
from report.models import Report
from account.models import Setting
import pytz

def send_alert():
    lines = Line.objects.filter(include_cron=True)
    period = Setting.objects.get(name='check_for_minutes').value
    algeria_timezone  = pytz.timezone('Africa/Algiers')
    current_time = datetime.now(algeria_timezone)
    today = datetime.today().date()

    for line in lines:
        for shift in line.shifts():
            shift_end_time = time(shift.hour_end, shift.minutes_end)
            allowed_delay = timedelta(minutes=line.allowed_delay)
            threshold = algeria_timezone.localize(datetime.combine(datetime.today(), shift_end_time) + allowed_delay)
            threshold_limit = algeria_timezone.localize(datetime.combine(datetime.today(), shift_end_time) + allowed_delay + timedelta(minutes=int(period)))

            if threshold <= current_time <= threshold_limit:
                if shift.hour_start > shift.hour_end:
                    yesterday = datetime.now() - timedelta(days=1)
                    alert = not Report.objects.filter(line=line, shift=shift, prod_day=yesterday.strftime('%Y-%m-%d')).exists()
                else:
                    alert = not Report.objects.filter(line=line, shift=shift, prod_day=today).exists()
                
                if line.site.address:
                    recipient_list = line.site.address.split('&')
                else:
                    recipient_list = ['benshamou@gmail.com']

                subject = 'Notification d\'alerte ' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                message = '''<p>Le rapport du shift [''' + shift.__str__() + '''] du ligne '''+line.__str__()+'''<b> n'est pas encore créé.</b>'''

                formatHtml = format_html(message)
                if alert:
                    #print('HERE', message, '\n', line, shift ,'\n' ,threshold , '\n', current_time  , '\n', threshold_limit)
                    send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)