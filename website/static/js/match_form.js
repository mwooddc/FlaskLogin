
// Define players in the broader scope to make it accessible inside addMatch
var players = null;

// Function to parse players data
function loadPlayersData() {
    var playersdata = document.getElementById('players').textContent;
    players = JSON.parse(playersdata);
    console.log(players);

}

function addMatch() {
    var playersdata = document.getElementById('players').textContent;
    var players = JSON.parse(playersdata);
    let container = document.getElementById("match-fields");
    let formCount = container.children.length;

    let newUserForm = document.createElement("div");
    newUserForm.setAttribute("class", "form-group lightgrey padding_top_10");
    newUserForm.setAttribute("id", `match${formCount}`);

    let row = document.createElement("div");
    row.className = "row";

    function createFormElement(elementType, name, classes, labelText, options = [], type = 'text', placeholder = '', min = '', defaultValue = '') {
        let col = document.createElement("div");
        col.className = classes;
        
        if (labelText) {
            let label = document.createElement("label");
            label.textContent = labelText;
            col.appendChild(label); // Append the label to the column before the input/select element
        }
        
        let element = document.createElement(elementType);
        element.name = name;
        element.className = 'form-control';
        if (elementType === 'input') {
            element.type = type;
            if (placeholder) element.placeholder = placeholder;
            if (min) element.min = min;
            element.value = defaultValue; // Set default value if provided, especially important for 'number' inputs
        }
        
        if (elementType === 'select' && options.length) {
            options.forEach(option => {
                let opt = document.createElement("option");
                opt.value = option.value;
                opt.textContent = option.label;
                element.appendChild(opt);
            });
        }
        
        col.appendChild(element);
        return col;
    }
    

    let playerOptions = Object.entries(players).map(([id, name]) => ({ value: id, label: name }));

    row.appendChild(createFormElement('select', `match[${formCount}][player1_name]`, 'col-sm-6 col-lg-2', 'Player 1 Name', playerOptions));
    row.appendChild(createFormElement('select', `match[${formCount}][player2_name]`, 'col-sm-6 col-lg-2', 'Player 2 Name', playerOptions));
    row.appendChild(createFormElement('select', `match[${formCount}][singles_or_doubles]`, 'col-sm-6 col-lg-2', 'Singles or Doubles', [{ value: 'Singles', label: 'Singles' }, { value: 'Doubles', label: 'Doubles' }]));
    // "Sets Played" field with min value of 1 and default value of 0
    row.appendChild(createFormElement('input', `match[${formCount}][sets_played]`, 'col-sm-6 col-lg-2', 'Sets Played', [], 'number', '', '1', '0'));

    // "Sets Won" field with min value of 0 and default value of 0
    row.appendChild(createFormElement('input', `match[${formCount}][sets_won]`, 'col-sm-6 col-lg-2', 'Sets Won', [], 'number', '', '0', '0'));

    row.appendChild(createFormElement('select', `match[${formCount}][won_or_lost]`, 'col-sm-6 col-lg-2', 'Won or Lost', [{ value: 'Won', label: 'Won' }, { value: 'Lost', label: 'Lost' }]));

    newUserForm.appendChild(row);

    // Correct placement and definition of commentRow
    let commentRow = document.createElement("div");
    commentRow.className = "form-group lightgrey padding_top_10";

    let commentLabel = document.createElement("label");
    commentLabel.textContent = 'Comment';
    commentRow.appendChild(commentLabel);

    let comment = document.createElement("textarea");
    comment.name = `match[${formCount}][comment]`;
    comment.className = 'form-control';
    comment.placeholder = 'Comment';
    commentRow.appendChild(comment);

    newUserForm.appendChild(commentRow);

    // Buttons on their own line
    let buttonRow = document.createElement("div");
    buttonRow.className = "form-group lightgrey padding_top_10 d-flex justify-content-between";

    let removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "btn maroon-btn";
    removeButton.textContent = "Remove Match";
    removeButton.onclick = function() { remove_match(`match${formCount}`); };
    buttonRow.appendChild(removeButton);

    newUserForm.appendChild(buttonRow);

    container.appendChild(newUserForm);
}





function remove_match(formId) {
    const formToRemove = document.getElementById(formId);
    formToRemove.remove();
}
