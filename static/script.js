document.addEventListener("DOMContentLoaded", function() {

    console.log("JS chargé");

    const form = document.querySelector("form");

    if (!form) return;

    const champNom = document.querySelector("input[name='nom']");
    const champDescription = document.querySelector("textarea[name='description']");

    // Validation
    function validerChamp(champ, condition, message) {

        let erreur = champ.parentElement.querySelector(".message-erreur");

        if (!condition) {

            if (!erreur) {
                erreur = document.createElement("p");
                erreur.classList.add("message-erreur");
                champ.parentElement.appendChild(erreur);
            }

            erreur.textContent = message;

            champ.classList.add("champ-invalide");

            return false;

        } else {

            if (erreur) erreur.remove();

            champ.classList.remove("champ-invalide");

            return true;
        }
    }

    // Temps réel
    champNom.addEventListener("input", function() {
        validerChamp(
            champNom,
            champNom.value.trim().length >= 4,
            "Le nom doit contenir au moins 4 caractères."
        );
    });

    champDescription.addEventListener("input", function() {
        validerChamp(
            champDescription,
            champDescription.value.trim().length >= 10,
            "La description doit contenir au moins 10 caractères."
        );
    });

    // Submit
    form.addEventListener("submit", function(evenement) {

        const nomOk = validerChamp(
            champNom,
            champNom.value.trim().length >= 4,
            "Le nom doit contenir au moins 4 caractères."
        );

        const descriptionOK = validerChamp(
            champDescription,
            champDescription.value.trim().length >= 10,
            "La description doit contenir au moins 10 caractères."
        );

        if (!nomOk || !descriptionOK) {
            evenement.preventDefault();
            return;
        }
    });

});