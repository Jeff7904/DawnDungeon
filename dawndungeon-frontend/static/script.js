$(document).ready(function() {
    var token = "{{ access_token }}";
    $.ajax({
        url: "http://localhost:8080/users/me",
        type: "GET",
        datatype: "json",
        // data: JSON.stringify({ "cmd": cmd }),
        headers : {
            "Authorization": "Bearer " + token,
        },
        contentType: "application/json",
        success: function(response) {
            // Handle the response from the server
            // alert(response)
            // $("#output").append(response);
        }, 
        error: function(error) {
            console.log("Bearer " + token)
            console.log(error);
            alert(error)
        }
    });

    // $.ajax({
    //     type: "POST",
    //     url: "http://localhost:8080/session/create-random",
    //     // data: JSON.stringify({ "cmd": cmd }),
    //     headers : {
    //         "Authentication": "Bearer " + token
    //     },
    //     contentType: "application/json",
    //     success: function(response) {
    //         // Handle the response from the server
    //         alert(response)
    //         // $("#output").append(response);
    //     }, 
    //     error: function(error) {
    //         console.log(error);
    //         alert(error)
    //     }
    // });

    $("#cmd").focus();
    $("#cmd").keypress(function(e) {
        if(e.which == 13) { // if user press enter
            var cmd = $("#cmd").val();
            $("#output").append("<div>" + cmd + "</div>");
            $("#cmd").val("");

            // Send the cmd variable to the server using AJAX
            $.ajax({
                type: "POST",
                url: "localhost:8080/session/create-random",
                // data: JSON.stringify({ "cmd": cmd }),
                headers : {
                    "Authentication": "Bearer {{ access_token }}"
                },
                contentType: "application/json",
                success: function(response) {
                    // Handle the response from the server
                    alert(response)
                    // $("#output").append(response);
                }, 
                error: function(error) {
                    console.error(error);
                    alert(error)
                }
            });
        }
    });

    $.getJSON("information.json", function(data){ // Read Json file
        character = data.metadata.character
        inventory = character.inventory
        quests = character.quests

        $(".debug-content").html(JSON.stringify(data, null, '\t')).hide();

        $(".character-attribute").html(
            "Name: " +  character.name + "<br/>" +
            "Age: " + character.age + "<br/>" +
            "Level: " + character.level + "<br/>" +
            "Coins: " + character.coins + "<br/>" +
            "Health: " + character.current_health + '/' + character.max_health + "<br/>"
        );

        // List all weapons
        var weaponsList = ""
        $.each(inventory, function(i, weapon){
            weaponsList += "<div class='btn btn-dark btn-sm m-1 weapon'>" + weapon.name + "</div>" + '\n';
        })

        $(".inventory").html(weaponsList)

        $(".weapon").click(function(){
            // Get the index of the clicked button
            var weaponIndex = $(this).index();
            weapon = inventory[weaponIndex]
            alert("Description: " + weapon.name + '\n' + "Damage: " + weapon.damage)
        })

        // List all quests
        var questLines = ""
        $.each(quests, function(i, quest){
            questLines += "<div class='btn btn-dark btn-sm m-1 quest'>" + quest.title + "</div>" + '\n';
        })

        $(".quests").html(questLines)

        $(".quest").click(function(){
            // Get the index of the clicked button
            var questIndex = $(this).index();
            quest = quests[questIndex]
            alert("Description: " + quest.description + '\n' + "Rewards: " + quest.rewards.coins + " coins" + '\n' + "Items: " + getItemNames(quest.rewards.items))
        })

        function getItemNames(items) {
            var itemNames = '';
            $.each(items, function(index, item) {
                itemNames += '\n' + item.name;
            });
            return itemNames;
        }

    }).fail(function(){
        console.log("An error has occurred.");
    })

    $(".debug-show").click(function(){
        $(".debug-content").toggle("slow")
    });
});