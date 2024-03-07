
// Define players in the broader scope to make it accessible inside addMatch
var players = null;

// Function to parse players data
function loadPlayersData() {
    var playersdata = document.getElementById('players').textContent;
    players = JSON.parse(playersdata);
    console.log(players);

}

function addMatch() {

    // Access the script id players from test.html which contains the data set
    // I need to do it this way as you can not use Jinja in an external js file
    var playersdata = document.getElementById('players').textContent;
    var players = JSON.parse(playersdata);
    console.log(players);

    let container = document.getElementById("match-fields");
    let formCount = container.children.length;
    console.log(formCount);
    


    // Create a new div element for the new user form
    let newUserForm = document.createElement("div");
    newUserForm.setAttribute("id", `match${formCount}`);



    // Create Player 1 input select element
    let player1_name = document.createElement("select");
    player1_name.setAttribute("name", `match[${formCount}][player1_name]`);
    player1_name.setAttribute("id", "player1_name"); // Setting the ID for the select element, useful for label association

    // Iterate over players dictionary to create and append option elements
    Object.entries(players).forEach(function([user_id, user_name]) {
        let option = document.createElement("option");
        option.value = user_id;
        option.textContent = user_name;
        player1_name.appendChild(option);
    });

    // Append the select element to the newUserForm
    newUserForm.appendChild(player1_name);




    // Create Player 2 input select element
    let player2_name = document.createElement("select");
    player2_name.setAttribute("name", `match[${formCount}][player2_name]`);
    player2_name.setAttribute("id", "player2_name"); // Setting the ID for the select element, useful for label association

    // Iterate over players dictionary to create and append option elements to player2_name select
    Object.entries(players).forEach(function([user_id, user_name]) {
        let option = document.createElement("option");
        option.value = user_id; // The user_id is the key in the players dictionary
        option.textContent = user_name; // The user_name is the value in the players dictionary
        player2_name.appendChild(option); // Append the option to the player2_name select element
    });


    // Append the select element to the newUserForm
    newUserForm.appendChild(player2_name);



    // Create Singles or Doubles input
    let singles_or_doubles = document.createElement("select");
    singles_or_doubles.setAttribute("name", `match[${formCount}][singles_or_doubles]`);
    singles_or_doubles.required = true;
    // Create the first option element for "Singles"
    let option1 = document.createElement("option");
    option1.value = "Singles";
    option1.textContent = "Singles";
    singles_or_doubles.appendChild(option1); // Append option1 to the select element
    // Create the second option element for "Doubles"
    let option2 = document.createElement("option");
    option2.value = "Doubles";
    option2.textContent = "Doubles";
    singles_or_doubles.appendChild(option2); // Append option2 to the select element
    newUserForm.appendChild(singles_or_doubles);



    // Create Sets Played input
    let sets_played = document.createElement("input");
    sets_played.setAttribute("type", "number");
    sets_played.setAttribute("id", "sets_played"); 
    sets_played.setAttribute("name", `match[${formCount}][sets_played]`);
    sets_played.setAttribute("min", "1"); // Set the minimum value to 1
    sets_played.setAttribute("placeholder", "Sets Played");
    sets_played.required = true; // Mark the field as required
    newUserForm.appendChild(sets_played);



    // Create Sets Won input
    let sets_won = document.createElement("input");
    sets_won.setAttribute("type", "number");
    sets_won.setAttribute("id", "sets_won");
    sets_won.setAttribute("name", `match[${formCount}][sets_won]`);
    sets_won.setAttribute("min", "0"); // Set the minimum value to 1
    sets_won.setAttribute("placeholder", "Sets Won");
    sets_won.required = true; // Mark the field as required
    newUserForm.appendChild(sets_won);



    // Create the won or lost input
    let won_or_lost = document.createElement("select");
    won_or_lost.setAttribute("id", "won_or_lost");
    won_or_lost.setAttribute("name", `match[${formCount}][won_or_lost]`);
    won_or_lost.required = true; // Mark the field as required
    let wonOption = document.createElement("option");
    wonOption.value = "Won";
    wonOption.textContent = "won";
    won_or_lost.appendChild(wonOption);
    let lostOption = document.createElement("option");
    lostOption.value = "Lost";
    lostOption.textContent = "Lost";
    won_or_lost.appendChild(lostOption);
    newUserForm.appendChild(won_or_lost);




    // Create the comments input
    let comment = document.createElement("textarea");
    comment.setAttribute("id", "comment");
    comment.setAttribute("name", `match[${formCount}][comment]`);
    comment.setAttribute("placeholder", "Comment");
    newUserForm.appendChild(comment);




    // Create Remove button
    let removeButton = document.createElement("button");
    removeButton.setAttribute("type", "button");
    removeButton.onclick = function() { remove_match(`match${formCount}`); };
    removeButton.textContent = "Remove Match";
    newUserForm.appendChild(removeButton);

    // Append the new user form div to the container
    container.appendChild(newUserForm);
}

function remove_match(formId) {
    const formToRemove = document.getElementById(formId);
    formToRemove.remove();
}
