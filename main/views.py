from django.shortcuts import render, HttpResponse
from purepython.gptsrs import (
    generate_full_sentence,
    to_native_language,
    from_native_language,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)
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
                "response": feedback
                # + "\n"
                + f"\n"
                + f"\nPhrase: {phrase_object.text}"
                + f"\nCosine Similarity: {str(round(cosine_similarity,4))}"
                + f"\nModel: {OPENAI_EMBEDDINGS_MODEL}",
            },
        )

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
    native_language = dict(LANGUAGE_CHOICES)[native_language_code]
    working_on = dict(LANGUAGE_CHOICES)[working_on_code]

    if len(qs) == 0:
        # return HttpResponse(
        #     "All least one phrase is required for app to work correctly."
        # )
        return render(
            request,
            "prompt.html",
            {
                "english_sentence": "All least one phrase is required for app to work correctly.",
                "no_phrases": True,
            },
        )

    next_phrase = qs[0]

    full_working_on_sentence = generate_full_sentence(
        next_phrase.text, working_on=working_on
    )
    print(full_working_on_sentence)
    print(full_working_on_sentence)
    print(full_working_on_sentence)
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
        {"english_sentence": request.session["equivalent_native_language_sentence"]},
    )
