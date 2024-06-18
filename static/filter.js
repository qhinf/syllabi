function moduleFilterSubmitted(event) {
    event.preventDefault()
}

function filterKeydowned(event) {
    if (event.key === "Escape" && event.target.value !== "") {
        event.target.value = ""
        filterModules("")
        event.preventDefault()
    }
}

function resetFilter() {
    document.querySelector("input[name='filter']").value = ""
    filterModules("")
}

function filterModules(filterText) {
    let anyVisible = false
    for (const module of document.querySelectorAll(".modules > article")) {
        if (
            filterText === "" || 
            module.getAttribute("data-title").toLowerCase().includes(filterText.toLowerCase()) ||
            module.getAttribute("data-slug").toLowerCase().includes(filterText.toLowerCase())
        ) {
            module.classList.toggle("hidden", false)
            anyVisible = true
        } else {
            module.classList.toggle("hidden", true)
        }
    }

    if (anyVisible) {
        document.getElementById("modules_notfound").classList.toggle("hidden", true)
    } else {
        document.getElementById("modules_notfound").classList.toggle("hidden", false)
    }
}

window.addEventListener("keypress", (event) => {
    if (event.key === "/") {
        document.querySelector("input[name='filter']").focus()
        event.preventDefault()
    }
})