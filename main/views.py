from django.shortcuts import render, HttpResponse
from purepython.gptsrs import (
    generate_full_sentence,
    to_english,
    from_english,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)
from main.models import Phrase

# phrase_list = ["en cuanto a"]


def prompt_view(request):
    if request.method == "POST":
        attempted_translation = request.POST.get("prompt", "")
        # response_text = prompt + "yes we can"
        embeddings = get_embeddings(
            [request.session.get("full_spanish_sentence", ""), attempted_translation]
        )
        cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        # print(attempted_translation)
        feedback = get_feedback(
            request.session.get("equivalent_english_sentence", ""),
            attempted_translation,
        )

        phrase_object = Phrase.objects.get(id=request.session.get("phrase_id", ""))
        phrase_object.cosine_similarity = cosine_similarity
        phrase_object.save()

        return render(
            request,
            "prompt.html",
            {
                "english_sentence": request.session["equivalent_english_sentence"],
                "attempted_translation": attempted_translation,
                "response": feedback
                + "\n\nCosine Similarity: "
                + str(cosine_similarity),
            },
        )

    # GET
    # Get most relevant phrase
    qs = Phrase.objects.all()

    if len(qs) == 0:
        return HttpResponse(
            "All least one phrase is required for app to work correctly."
        )

    next_phrase = qs[0]

    full_spanish_sentence = generate_full_sentence(next_phrase.text)
    equivalent_english_sentence = to_english(full_spanish_sentence)
    # attempted_translation = input(f"{equivalent_english_sentence} >>> ")
    # embeddings = get_embeddings([full_spanish_sentence, attempted_translation])
    # cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])

    # print(full_spanish_sentence)
    # print(equivalent_english_sentence)

    # store session variables
    request.session["phrase_id"] = next_phrase.id
    request.session["full_spanish_sentence"] = full_spanish_sentence
    request.session["equivalent_english_sentence"] = equivalent_english_sentence

    return render(
        request,
        "prompt.html",
        {"english_sentence": request.session["equivalent_english_sentence"]},
    )
