from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
# Create your models here.


class UserRquestSite(models.Model):
    user=   models.ForeignKey(User)
    fertilizer= models.CharField(max_length=100)
    current_crop= models.CharField(max_length=100)
    season =    models.IntegerField()
    soiltype=   models.CharField(max_length=100)
    tilltype=   models.CharField(max_length=100)
    latitude=   models.CharField(max_length=100)
    longitude=  models.CharField(max_length=100)
    climate =   models.CharField(max_length=100)
    prev_crop=  models.CharField(max_length=100)
    price_mean= models.FloatField(null=True)
    price_std=  models.FloatField(null=True)
    costmean=   models.FloatField(null=True)
    coststd=    models.FloatField(null=True)
    request_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.soiltype + self.climate

    # class Meta:
    #       db_table = 'userrquestsite'


class UserTransaction(models.Model):

    usersite = models.OneToOneField(
        UserRquestSite,
        verbose_name="user request site to user trans mapping",
    )
    user = models.ForeignKey(User)
    #'0:Pending, 1: Completed'
    status = models.IntegerField(null=True,default=0)
    creation_date=models.DateField(auto_now_add=True)
    retry_count=models.IntegerField(null=True, default=0)
    #'Y:Yes,N:No'
    isEmailSent=models.CharField(max_length=1,default='N')
    request_process_time=models.IntegerField(null=True)

    # class Meta:
    #      db_table = 'usertransaction'


class SiteField(models.Model):
    Site_Field=models.CharField(max_length=200)
    BDoriginale=models.CharField(max_length=100)
    Province=models.CharField(max_length=100)
    Region=models.CharField(max_length=200)
    Town=models.CharField(max_length=100)
    Site=models.CharField(max_length=100)
    Field=models.IntegerField()

class PlotYield(models.Model):
    SiteFieldId=models.ForeignKey(SiteField)
    LAT=models.FloatField(null=True)
    LONG=models.FloatField(null=True)
    Year=models.IntegerField(null=True)
    SoilType=models.CharField(max_length=100)
    SoilTexture_cls=models.CharField(null=True,max_length=100)
    ClayRatio=models.IntegerField(null=True)
    SOM=models.FloatField(null=True)
    TillPractice=models.CharField(null=True,max_length=100)
    TillType=models.CharField(null=True,max_length=100)
    PrevCrop=models.CharField(null=True,max_length=100)
    PrevContribN_cls=models.CharField(null=True,max_length=100)
    PrevContribN_int=models.IntegerField(null=True)
    CHU=models.IntegerField(null=True)
    PPT=models.IntegerField(null=True)
    AWDR=models.FloatField(null=True)
    Nrate=models.IntegerField(null=False)
    Yield=models.FloatField(null=False)
