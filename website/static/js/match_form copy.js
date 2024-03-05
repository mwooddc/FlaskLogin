function addUserForm() {
    let container = document.getElementById("userForms");
    let formCount = container.children.length;
    console.log(formCount);

    // Create a new div element for the new user form
    let newUserForm = document.createElement("div");
    newUserForm.setAttribute("id", `form${formCount}`);

    // Create ID input
    let idInput = document.createElement("input");
    idInput.setAttribute("type", "text");
    idInput.setAttribute("name", `users[${formCount}][id]`);
    idInput.setAttribute("placeholder", "ID");
    newUserForm.appendChild(idInput);

    // Create Name input
    let nameInput = document.createElement("input");
    nameInput.setAttribute("type", "text");
    nameInput.setAttribute("name", `users[${formCount}][name]`);
    nameInput.setAttribute("placeholder", "Name");
    newUserForm.appendChild(nameInput);

    // Create Age input
    let ageInput = document.createElement("input");
    ageInput.setAttribute("type", "text");
    ageInput.setAttribute("name", `users[${formCount}][age]`);
    ageInput.setAttribute("placeholder", "Age");
    newUserForm.appendChild(ageInput);

    // Create Remove button
    let removeButton = document.createElement("button");
    removeButton.setAttribute("type", "button");
    removeButton.onclick = function() { removeUserForm(`form${formCount}`); };
    removeButton.textContent = "Remove User";
    newUserForm.appendChild(removeButton);

    // Append the new user form div to the container
    container.appendChild(newUserForm);
}

function removeUserForm(formId) {
    const formToRemove = document.getElementById(formId);
    formToRemove.remove();
}