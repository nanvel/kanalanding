/* babel static/app.js -o static/app.min.js -s --presets=es2015,stage-0,babili --no-babelrc */

let submitData = (url, {name, email, message, recaptchaResponse, onSuccess, onError}) => {
    let http = new XMLHttpRequest()
    let params = `name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&message=${encodeURIComponent(message)}&recaptchaResponse=${encodeURIComponent(recaptchaResponse)}`
    http.open("POST", url, true);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    http.onreadystatechange = function() {
        if(http.readyState == 4) {
            if (http.status == 200) {
                onSuccess()
            } else {
                onError()
            }
        }
    }
    http.send(params)
}

var captchaIsVisible = false


let setStatus = (status, color) => {
    let errorsContainer = document.getElementById("status")
    errorsContainer.style.color = color
    errorsContainer.innerText = status
}


let checkCaptcha = (target) => {
    if (RECATCHA_LOADED && !captchaIsVisible && target.value.length > 0) {
        captchaIsVisible = true
        grecaptcha.render("recaptcha-container", {'sitekey': RECAPTCHA_SITE_KEY})
    }
}


document.getElementById("name").onkeyup = (event) => checkCaptcha(event.target)
document.getElementById("message").onkeyup = (event) => checkCaptcha(event.target)


document.getElementById("feedback-form").onsubmit = (event) => {
    event.preventDefault()

    if (captchaIsVisible) {

        let recaptchaResponse = grecaptcha.getResponse()

        if (recaptchaResponse.length > 0) {

            let name = document.getElementById("name")
            let email = document.getElementById("email")
            let message = document.getElementById("message")

            let submitButton = document.getElementById("submit-button")
            submitButton.disabled = true

            submitData(
                event.target.action,
                {
                    name: name.value,
                    email: email.value,
                    message: message.value,
                    recaptchaResponse,
                    onSuccess: () => {
                        setStatus("Sent.", "green")
                        submitButton.disabled = false
                        name.value = ""
                        email.value = ""
                        message.value = ""
                        grecaptcha.reset()
                    },
                    onError: () => {
                        setStatus("Something went wrong.", "red")
                        submitButton.disabled = false
                        grecaptcha.reset()
                    }
                }
            )
        } else {
            setStatus("Please enter captcha.", "red")
        }
    }
}

let year = (new Date()).getFullYear()
Array.from(document.getElementsByClassName("year")).forEach((element) => {
    element.innerText = year
})
