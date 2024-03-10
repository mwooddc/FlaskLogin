var matchCounter = 1;
        
function addMatch() {
    var container = document.getElementById("match-fields");
    var matchDiv = document.createElement("div");
    matchDiv.innerHTML = `
        <div class="match">
            <!-- Dropdown list for Player 1 -->
            <label for="player1_name_${matchCounter}">Player 1:</label>
            <select id="player1_name_${matchCounter}" name="player1_name_${matchCounter}">
                {% for user_id, user_name in match_form.player1_name_0.choices %}
                <option value="{{ user_id }}">{{ user_name }}</option>
                {% endfor %}
            </select>






            
            <!-- Dropdown list for Player 2 -->
            <label for="player2_name_${matchCounter}">Player 2:</label>
            <select id="player2_name_${matchCounter}" name="player2_name_${matchCounter}">
                {% for user_id, user_name in match_form.player2_name_0.choices %}
                <option value="{{ user_id }}">{{ user_name }}</option>
                {% endfor %}
            </select>
            <!-- Display errors for player1_name -->
            {% if match_form.player2_name_0.errors %}
            {% for error in match_form.player2_name_0.errors %}
                <div style="color: red;">{{ error }}</div>
            {% endfor %}
            {% endif %}

            <!-- Other match fields -->
            <label for="singles_or_doubles_${matchCounter}">Singles or Doubles:</label>
            <select id="singles_or_doubles_${matchCounter}" name="singles_or_doubles_${matchCounter}" required>
                <option value="Singles">Singles</option>
                <option value="Doubles">Doubles</option>
            </select><br><br>

            <label for="sets_played_${matchCounter}">Sets Played:</label>
            <input type="number" id="sets_played_${matchCounter}" name="sets_played_${matchCounter}" min="1" required><br><br>

            <label for="sets_won_${matchCounter}">Sets Won:</label>
            <input type="number" id="sets_won_${matchCounter}" name="sets_won_${matchCounter}" min="0" required><br><br>

            <label for="won_or_lost_${matchCounter}">Won or Lost:</label>
            <select id="won_or_lost_${matchCounter}" name="won_or_lost_${matchCounter}" required>
                <option value="Won">won</option>
                <option value="Lost">Lost</option>
            </select><br><br>

            <label for="comment_${matchCounter}">Comment:</label>
            <textarea id="comment_${matchCounter}" name="comment_${matchCounter}"></textarea><br><br>
        </div><br>
    `;
    container.appendChild(matchDiv);
    matchCounter++;
}