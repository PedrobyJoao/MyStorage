// Adding a NEW item (Modal Action)
function newitem_button(){
    // Checking if input is not blank
    if (document.getElementById('item_action').value == '' || document.getElementById('new_quantity').value == '' || document.getElementById('new_price').value == ''){
        alert("You can't leave blank inputs!");
    }
    else{
        // Opening modal
        let myModal = new bootstrap.Modal(document.getElementById('modal-newitem'), {});
        myModal.show();

        // Giving values (item, qtd, price) which will be send to routes
        document.getElementById('new_item').value = document.getElementById('item_action').value;
        document.getElementById('modalnew_quantity').value = document.getElementById('new_quantity').value;
        document.getElementById('modalnew_price').value = document.getElementById('new_price').value;
        document.getElementById('span_newitem').innerHTML = document.getElementById('new_item').value;
        document.getElementById('span_newquantity').innerHTML = document.getElementById('modalnew_quantity').value;

        // Formating price for modal
        price_value = parseFloat(document.getElementById('new_price').value)
        formatted_value = price_value.toFixed(2)
        document.getElementById('span_newmodalprice').innerHTML = formatted_value;
    }
}

// Add/Remove snipet when adding/removing through the TABLE
function modal_button(value, item, quantity, price){
    // If the user let blank inputs
    if (document.getElementById(quantity).value == '' || document.getElementById(price).value == ''){
        alert("You can't leave blank inputs!");
    }
    else{
        // Open modal
        let myModal = new bootstrap.Modal(document.getElementById('modal-storage'), {});
        myModal.show();
        // Value ADD or REMOVE that will send to routes.py
        document.getElementById('modal_button').value = value;
        // Writing process in <span>
        if(value == 'add'){
            document.getElementById('add-removewrite').innerHTML = "add";
        }
        else if(value == 'remove'){
            document.getElementById('add-removewrite').innerHTML = "remove";
        }
        // Giving values (item, qtd, price) which will be send to routes
        price_value = document.getElementById(price).value;
        document.getElementById('modal_quantity').value = document.getElementById(quantity).value;
        document.getElementById('modal_price').value = price_value;
        document.getElementById('modal_item').value = document.getElementById(item).value;
        // Writing process in <span>
        document.getElementById('span_modalqtd').innerHTML = document.getElementById(quantity).value;
        document.getElementById('span_modalitem').innerHTML = document.getElementById(item).value;

        // Formating price for modal
        price_value = parseFloat(price_value)
        formatted_value = price_value.toFixed(2)
        document.getElementById('span_modalprice').innerHTML = formatted_value;
    }
}