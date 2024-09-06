import os
import numpy as np

# from django.db.models.expressions import RawSQL
# from django.db.models.functions import Abs, Coalesce
from django.db.models.functions import Abs
from django.shortcuts import render, HttpResponse
from purepython.gptsrs import (
    generate_full_sentence,
    to_native_language,
    from_native_language,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)

# from django.db.models import F
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value, StdDev
from main.models import Phrase
from accounts.models import LANGUAGE_CHOICES
from purepython.gptsrs import OPENAI_EMBEDDINGS_MODEL

# phrase_list = ["en cuanto a"]


def prompt_view(request):
    if request.method == "POST":
        attempted_translation = request.POST.get("prompt", "")
        # response_text = prompt + "yes we can"
        embeddings = get_embeddings(
            [request.session.get("full_working_on_sentence", ""), attempted_translation]
        )
        cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        # print(attempted_translation)
        feedback = get_feedback(
            request.session.get("equivalent_native_language_sentence", ""),
            attempted_translation,
            working_on=request.session.get("working_on", ""),
            native_language=request.session.get("native_language", ""),
        )

        phrase_object = Phrase.objects.get(id=request.session.get("phrase_id", ""))
        phrase_object.cosine_similarity = cosine_similarity
        if phrase_object.user == request.user:  # only if user is logged in
            phrase_object.save()

        return render(
            request,
            "prompt.html",
            {
                "english_sentence": request.session[
                    "equivalent_native_language_sentence"
                ],
                "attempted_translation": attempted_translation,
                "response": feedback,
                # + "\n"
                # + f"\n"
                # + f"\nPhrase: {phrase_object.cleaned_text}"
                # + f"\nCosine Similarity: {str(round(cosine_similarity,4))}"
                # + f"\nModel: {OPENAI_EMBEDDINGS_MODEL}",
                "phrase": phrase_object.cleaned_text,
                "cosine_similarity": str(round(cosine_similarity, 4)),
                "model": OPENAI_EMBEDDINGS_MODEL,
            },
        )

    ########################################################################
    # GET
    # Get most relevant phrase
    # print(request.user)

    if request.user.is_authenticated:
        native_language_code = request.user.native_language
        working_on_code = request.user.working_on
        qs = Phrase.objects.filter(user=request.user, language=working_on_code)
    else:
        native_language_code = "en"
        working_on_code = "es"
        qs = Phrase.objects.filter(language=working_on_code)
        qs = qs.filter(cosine_similarity__isnull=False)
    native_language = dict(LANGUAGE_CHOICES)[native_language_code]
    working_on = dict(LANGUAGE_CHOICES)[working_on_code]

    if len(qs) == 0:
        # Handle empty data
        return render(
            request,
            "prompt.html",
            {
                "english_sentence": "All least one phrase is required for app to work correctly.",
                "no_phrases": True,
            },
        )

    # Update que_score
    # print("""qs.update(cosine_similarity=F("cosine_similarity") + 1)""")
    qs_values = qs.values_list("cosine_similarity")
    # Step 2: Exclude None values
    first_elements = [t[0] for t in qs_values]
    filtered_values = [value for value in first_elements if value is not None]

    # Step 3: Convert to a NumPy array
    numpy_array = np.array(filtered_values)

    # Step 4: Calculate the mean value
    if numpy_array.size > 0:
        mean_value = float(np.mean(numpy_array)) + float(os.environ["FABULARI_PARAM0"])
        stddev_value = float(np.std(numpy_array)) * float(os.environ["FABULARI_PARAM1"])
    else:
        mean_value = 0.50 + float(os.environ["FABULARI_PARAM0"])
        stddev_value = 0.25 * float(os.environ["FABULARI_PARAM1"])

    # if request.user.is_authenticated:
    #     qs.update(
    #         noise=RawSQL(  # for MySQL
    #             f"{mean_value} + {stddev_value} * SQRT(-2 * LOG(RAND())) * COS(2 * PI() * RAND())",
    #             [],
    #         )
    #     )
    #     qs.update(que_score=Coalesce(Abs(F("cosine_similarity") - F("noise")), 0))
    # else:
    print(numpy_array)
    print(mean_value)
    print(stddev_value)
    random_value = np.random.normal(loc=mean_value, scale=stddev_value)
    print(random_value)
    qs = qs.annotate(
        noise_for_anon_user=ExpressionWrapper(
            Abs(F("cosine_similarity") - random_value), output_field=FloatField(),
        )
    ).order_by("noise_for_anon_user")

    # Generate template vars
    next_phrase = qs[0]

    full_working_on_sentence = generate_full_sentence(
        next_phrase.text, working_on=working_on
    )
    equivalent_native_language_sentence = to_native_language(
        full_working_on_sentence,
        working_on=working_on,
        native_language=native_language,
    )

    # store session variables
    request.session["phrase_id"] = next_phrase.id
    request.session["full_working_on_sentence"] = full_working_on_sentence
    request.session[
        "equivalent_native_language_sentence"
    ] = equivalent_native_language_sentence
    request.session["working_on"] = working_on
    request.session["native_language"] = native_language

    return render(
        request,
        "prompt.html",
        {
            "english_sentence": request.session["equivalent_native_language_sentence"],
            "working_on": working_on,
            "last_cosine_similarity": next_phrase.cosine_similarity
            if next_phrase.cosine_similarity
            else "N/A",
            "random_value": round(random_value, 4),
            "que_score": round(
                abs(float(next_phrase.cosine_similarity) - random_value), 4
            )
            if next_phrase.cosine_similarity
            else 0,
        },
    )
