import csv
from django.http import HttpResponse
from django.shortcuts import get_list_or_404
from main.models import Phrase
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required(login_url=reverse("admin:login"))
def export_phrases_to_csv_view(request):
    # You might want to add permission checks here
    # queryset = get_list_or_404(Phrase.objects.filter(user=request.user))
    queryset = Phrase.objects.filter(user=request.user)
    # queryset = queryset.filter(user=request.user)
    # data = list(Phrase.objects.filter(user=request.user).values())

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=phrase_list.csv"

    # Write BOM for UTF-8
    # response.write("\ufeff")

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "Raw Text",
            "Cleaned Text",
            "language",
            "Definition",
            "Example",
            "Cosine Similarity",
            # "Noise",
            # "Que Score",
        ]
    )  # Replace with your model field names
    # import pandas as pd

    # data = list(
    #     queryset.values(
    #         "text",
    #         "cleaned_text",
    #         "definition",
    #         "example_sentence",
    #         "cosine_similarity",
    #     )
    # )
    # df = pd.DataFrame(data)

    # Write data rows
    for obj in queryset:
        writer.writerow(
            [
                obj.text,
                obj.cleaned_text,
                obj.language,
                obj.definition,
                obj.example_sentence,
                obj.cosine_similarity,
                # obj.noise,
                # obj.que_score,
            ]
        )  # Replace with your model fields
    # df.to_csv(path_or_buf=response, index=False)
    # Write BOM for UTF-8
    # response.write("\ufeff")
    return response
