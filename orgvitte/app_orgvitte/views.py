from django.http import HttpResponse


def index(request):
    return HttpResponse("Андрюха, красавчик. Выеби эту преддипломную!!!")