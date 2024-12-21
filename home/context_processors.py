from home.models import WebSetup


def company_context(request):
    return {
        "company": WebSetup.objects.last(),
    }
