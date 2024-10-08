import os
import numpy as np
from django.conf import settings
from django.db.models.functions import Abs
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db.models import FloatField, F, ExpressionWrapper
from purepython.practice_translation import (
    generate_full_sentence,
    to_native_language,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)
from main.models import Phrase

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]

zero_to_ten_multiplier = 10  # score from 0 to 10 is more intuitive


def practice_translation_view(request, phrase_id=None):
    # Don't waste money on unauthenticated users
    if request.user.is_authenticated:
        openai_llm_model = request.user.openai_llm_model_complex_tasks
    else:
        openai_llm_model = settings.OPENAI_LLM_MODEL_SIMPLE_TASKS

    # if request.method == "POST" and phrase_id:
    #     return redirect("https://www.nytimes.com")
    if request.method == "POST":
        attempted_translation = request.POST.get("prompt", "")
        # print(attempted_translation)
        if attempted_translation == "":
            return redirect("prompt_view")
        # response_text = prompt + "yes we can"
        # print(attempted_translation)
        # print(attempted_translation)
        # print(request.session.get("full_working_on_sentence", ""))
        # print(
        #     [request.session.get("full_working_on_sentence", ""), attempted_translation]
        # )
        embeddings = get_embeddings(
            [
                request.session.get("full_working_on_sentence", ""),
                attempted_translation,
            ],
            openai_embeddings_model=settings.OPENAI_EMBEDDINGS_MODEL,
        )
        cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        # print(attempted_translation)
        # if request.user.is_authenticated:
        #     openai_llm_model = request.user.openai_llm_model_complex_tasks
        # else:
        #     openai_llm_model = settings.OPENAI_LLM_MODEL_SIMPLE_TASKS

        feedback = get_feedback(
            request.session.get("equivalent_native_language_sentence", ""),
            attempted_translation,
            request.session["phrase_cleaned_text"],
            working_on=request.session.get("working_on", ""),
            native_language=request.session.get("native_language", ""),
            openai_model=openai_llm_model,
        )

        phrase_object = Phrase.objects.get(id=request.session.get("phrase_id", ""))
        phrase_object.cosine_similarity = cosine_similarity
        if phrase_object.user == request.user:  # only if user is logged in
            phrase_object.save()

        return render(
            request,
            "practice_translation.html",
            {
                "phrase_id": phrase_id,
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
                "cosine_similarity": str(
                    round(cosine_similarity * zero_to_ten_multiplier, 1)
                ),
                "model": settings.OPENAI_EMBEDDINGS_MODEL,
            },
        )

    ########################################################################
    ########################################################################
    ########################################################################
    # GET
    # Get most relevant phrase
    # print(request.user)

    if request.user.is_authenticated:
        native_language = request.user.native_language
        working_on = request.user.working_on
        qs = Phrase.objects.filter(user=request.user, language=working_on)
    else:
        native_language = "en"
        working_on = "es"
        qs = Phrase.objects.filter(language=working_on)
        qs = qs.filter(cosine_similarity__isnull=False)
    native_language_verbose = dict(LANGUAGE_CHOICES)[native_language]
    working_on_verbose = dict(LANGUAGE_CHOICES)[working_on]

    if phrase_id:
        next_phrase = Phrase.objects.get(id=phrase_id)
        working_on_verbose = dict(LANGUAGE_CHOICES)[next_phrase.language]
        print(working_on_verbose)
        # random_value = request.session["random_value"]
    else:

        if len(qs) == 0:
            # Handle empty data
            return render(
                request,
                "practice_translation.html",
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
            mean_value = float(np.mean(numpy_array)) + float(
                os.environ["FABULARI_PARAM0"]
            )
            stddev_value = float(np.std(numpy_array)) * float(
                os.environ["FABULARI_PARAM1"]
            )
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
        # print(numpy_array)
        # print(mean_value)
        # print(stddev_value)
        random_value = np.random.normal(loc=mean_value, scale=stddev_value)
        # print(random_value)
        qs = qs.annotate(
            que_score=ExpressionWrapper(
                Abs(F("cosine_similarity") - random_value), output_field=FloatField(),
            )
        ).order_by("que_score")

        # Generate template vars
        # lowest que_score goes first
        next_phrase = qs[0]
        print("random_value: ", random_value)
        print("next_phrase.cosine_similarity: ", next_phrase.cosine_similarity)
        print("next_phrase.id: ", next_phrase.id)
        # request.session["random_value"] = random_value
        # request.session["prev_cosine_similarity"] = float(next_phrase.cosine_similarity)

        # return redirect(f"/{next_phrase.id}")

        # from django.utils.translation import activate

        # activate(request.user.native_language)
        # print("activate(request.user.native_language)")

        return redirect(reverse("practice_translation", args=[next_phrase.id]))

    full_working_on_sentence = generate_full_sentence(
        phrase=next_phrase.raw_text,
        working_on_verbose=working_on_verbose,
        openai_llm_model=openai_llm_model,
        # openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        # openai_model=request.user.openai_llm_model_complex_tasks,
    )
    equivalent_native_language_sentence = to_native_language(
        sentence=full_working_on_sentence,
        working_on_verbose=working_on_verbose,
        native_language_verbose=native_language_verbose,
        # openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        openai_llm_model=openai_llm_model,
        # openai_llm_model=request.user.openai_llm_model_complex_tasks,
    )

    # store session variables
    request.session["phrase_id"] = next_phrase.id
    request.session["phrase_cleaned_text"] = next_phrase.cleaned_text
    request.session["full_working_on_sentence"] = full_working_on_sentence
    request.session[
        "equivalent_native_language_sentence"
    ] = equivalent_native_language_sentence
    request.session["working_on"] = working_on_verbose
    request.session["native_language"] = native_language_verbose

    return render(
        request,
        "practice_translation.html",
        {
            "host_email": settings.EMAIL_HOST_USER,
            "phrase_id": phrase_id,
            "english_sentence": request.session["equivalent_native_language_sentence"],
            "working_on": working_on_verbose,
            # "last_cosine_similarity": round(
            #     request.session.get("prev_cosine_similarity") * zero_to_ten_multiplier,
            #     1,
            # )
            # if request.session.get("prev_cosine_similarity")
            # else None,
            # "random_value": round(
            #     request.session.get("random_value") * zero_to_ten_multiplier, 1
            # ),
            # "que_score": round(
            #     abs(
            #         float(request.session.get("prev_cosine_similarity"))
            #         - request.session.get("random_value")
            #     )
            #     * zero_to_ten_multiplier,
            #     1,
            # )
            # if request.session.get("prev_cosine_similarity")
            # else None,
        },
    )
