# We should all know what this is used for by now.
from django.core.mail import send_mail

# get_template is what we need for loading up the template for parsing.
from django.template.loader import get_template

# Templates in Django need a "Context" to parse with, so we'll borrow this.
# "Context"'s are really nothing more than a generic dict wrapped up in a
# neat little function call.
from django.template import Context
from django.core.mail import EmailMessage
from django.conf import settings as djangoSettings

def EmailResultsToUser(context,user):

    print('start, EmailResultsToUser')
    from_email = 'passagridss@gmail.com'
    subject = 'NumericAg - Please find results below!'
    to= [user.email]
    # Our send_mail call revisited. This time, instead of passing
    # a string for the body, we load up a template with get_template()
    # and render it with a Context of the variables we want to make available
    # to that template.
    try:
        # send_mail(
        #     'Team PASSApp, Please find results and reccomondation below !',
        #     get_template('emailtemplate.html').render(
        #         Context(context)
        #     ),
        #     from_email,
        #     ['sadanand.shinde@mail.mcgill.ca'],
        #     fail_silently=True
        # )

        message = get_template('emailtemplate.html').render(Context(context))
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        #msg.attach(filename='testimage.png',content=djangoSettings.STATIC_ROOT + '/images/profitfunction/profitfunction.png')
        msg.attach_file(djangoSettings.STATIC_ROOT + '/images/profitfunction/profitfunction'+user.first_name+'_'+str(user.id )+'.png')
        msg.attach_file(djangoSettings.STATIC_ROOT + '/images/profitfunction/ProfitSurfacePlot_' + user.first_name + '_' + str(user.id) + '.png')
        msg.content_subtype = 'html'
        msg.send()

        print('end, EmailResultsToUser sent successfully to user ',to)

    except Exception as exc:
        print('There is some exception in sending email in EmailResultsToUser(): ' + str(exc))
        return False

    return True

def emailNoMatchingSiteFoundtoUser(user):
    from_email = 'passagridss@gmail.com'
    subject = 'NumericAg – No records match your context parameters!'
    to = [user.email]
    try:
        message="Hello "+user.first_name+" \n We regret, no records match the context that you defined in the NumericAg application. Please reformulate the user inputs and try again!. \n NumericAg Team "
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.send()

    except Exception as exc:
        print('There is some exception in sending email in emailNoMatchingSiteFoundtoUser(): ' + str(exc))
        return False

    return True

def updateTransParams(rs, status,emailFlag,processTime):

    if  processTime is not None:
        print('processingTime: ' + str(processTime))
        hh,mm,ss= str(processTime).split(':')
        print('hh: '+ str(hh)+'mm: '+str(mm)+'ss: '+ str(ss))
        rs.request_process_time = mm

    rs.status = status
    rs.isEmailSent = emailFlag

    # request_process_time
    rs.save()


    return
