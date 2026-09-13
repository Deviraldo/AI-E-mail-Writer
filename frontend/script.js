// ============================================
// API URL
// ============================================

const API_URL =
    "http://127.0.0.1:8000";


// ============================================
// GET HTML ELEMENTS
// ============================================

const recipient =
    document.getElementById("recipient");

const purpose =
    document.getElementById("purpose");

const tone =
    document.getElementById("tone");

const keyPoints =
    document.getElementById("keyPoints");

const generateButton =
    document.getElementById("generateButton");

const loading =
    document.getElementById("loading");

const errorMessage =
    document.getElementById("errorMessage");

const resultSection =
    document.getElementById("resultSection");

const emailOutput =
    document.getElementById("emailOutput");

const characterCount =
    document.getElementById("characterCount");


// ============================================
// CHARACTER COUNTER
// ============================================

keyPoints.addEventListener(
    "input",
    function () {

        const count =
            keyPoints.value.length;

        characterCount.textContent =
            `${count} / 5000`;

    }
);


// ============================================
// GENERATE EMAIL
// ============================================

async function generateEmail() {

    // Get values from form

    const recipientValue =
        recipient.value.trim();

    const purposeValue =
        purpose.value.trim();

    const toneValue =
        tone.value;

    const keyPointsValue =
        keyPoints.value.trim();


    // ========================================
    // VALIDATION
    // ========================================

    if (!recipientValue) {

        showError(
            "Please enter the recipient."
        );

        return;
    }


    if (!purposeValue) {

        showError(
            "Please enter the purpose of the email."
        );

        return;
    }


    if (!keyPointsValue) {

        showError(
            "Please enter some important points."
        );

        return;
    }


    // ========================================
    // RESET UI
    // ========================================

    hideError();

    resultSection.classList.add(
        "hidden"
    );

    loading.classList.remove(
        "hidden"
    );

    generateButton.disabled = true;


    try {

        // ====================================
        // SEND REQUEST TO FASTAPI
        // ====================================

        const response = await fetch(
            `${API_URL}/generate-email`,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    recipient:
                        recipientValue,

                    purpose:
                        purposeValue,

                    tone:
                        toneValue,

                    key_points:
                        keyPointsValue

                })

            }
        );


        // ====================================
        // GET RESPONSE
        // ====================================

        const data =
            await response.json();


        // ====================================
        // CHECK FOR ERROR
        // ====================================

        if (!response.ok) {

            throw new Error(

                data.detail ||
                "Failed to generate email."

            );

        }


        // ====================================
        // DISPLAY EMAIL
        // ====================================

        emailOutput.textContent =
            data.email;


        resultSection.classList.remove(
            "hidden"
        );


    }

    catch (error) {

        console.error(error);

        showError(

            error.message ||
            "Could not connect to the backend."

        );

    }

    finally {

        loading.classList.add(
            "hidden"
        );

        generateButton.disabled =
            false;

    }

}


// ============================================
// COPY EMAIL
// ============================================

async function copyEmail() {

    const email =
        emailOutput.textContent;


    if (!email) {

        return;

    }


    try {

        await navigator.clipboard.writeText(
            email
        );


        const button =
            document.getElementById(
                "copyButton"
            );


        const originalText =
            button.textContent;


        button.textContent =
            "Copied!";


        setTimeout(
            function () {

                button.textContent =
                    originalText;

            },
            1500
        );


    }

    catch (error) {

        console.error(
            "Copy failed:",
            error
        );

    }

}


// ============================================
// SHOW ERROR
// ============================================

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );

}


// ============================================
// HIDE ERROR
// ============================================

function hideError() {

    errorMessage.classList.add(
        "hidden"
    );

}