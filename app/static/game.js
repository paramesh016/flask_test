var dict_words;
var score=0;
var max_score;
var found_values = [];
var is_past = "{{pastgame}}";
if (is_past=="yes"){ var found_val =  "{{ctx['found_val'] }}";}
var boogle_board = "{{ctx['board']}}";
$(document).ready(function(){
		debugger;
		var i;   	
		$('#alert_msg').hide();
		$('#found_list').hide();
		$('#reveal_words_div').hide();
		board = "{{ctx['board']}}";   	
		dict_words =  "{{ctx['board_val'] }}";
		$("#max_score").html(max_score);
		dict_words = dict_words.split('[')[1]
		dict_words = dict_words.split(']')[0]
		dict_words = dict_words.replace (/'/g, "");
		dict_words = dict_words.replace(/ /g,'')
		dict_words = dict_words.split(',')
		max_score = dict_words.length;
		$('#max_score').html('Total number of words present in the Boggle : '+max_score);
	for (i = 0; i < board.length; i++) {
	    val = '<tr>'		    
	    for(j=0;j<board[i].length; j++){
	    	val += '<td style="width:58px">'+board[i][j]+'</td>'		    	
	    	
	    }	
	val += '</tr>'        		    
	$('#boggle_table').append(val);
	}
	if (is_past=="yes"){
   		found_val = found_val.split('[')[1]
   		found_val = found_val.split(']')[0]
   		found_val = found_val.replace (/'/g, "");
   		found_val = found_val.replace(/ /g,'')
   		found_val = found_val.split(',')
		$.each(dict_words, function( index, value ) {
				$('#reveal_words_divs').append(value+',');
		});
		$('#reveal_words_divs').text(function (_,txt) {
    		return txt.slice(0, -1);
		});	
		$.each(found_val, function( index, value ) {
				$('#found_lists').append(value+',');
		});
		$('#found_lists').text(function (_,txt) {
    		return txt.slice(0, -1);
		});	
	}
});
$('#check_word').click(function(){
	$('#alert_msg').show();
	input_val = $('#usr').val().toUpperCase();
	if (input_val==""){
		setTimeout(function() { $('#alert_msg').hide(); }, 5000);
		$('#alert_msg').html('Enter a word and then press check!!');	
		return
	}
	valid_check = dict_words.includes(input_val);
	already_found = found_values.includes(input_val);
	if(valid_check && !already_found){
		score++;
		$('#found_list').show();			
		$('#user_score').html('Number of words found by you : '+score);
		found_values.push(input_val);
		setTimeout(function() { $('#alert_msg').hide(); }, 5000);
		$('#alert_msg').html('Nice Job, you found one');
		$("#found_list").append(input_val+ ' , ');
		$('#usr').val("");
	}
	else if (already_found) {
	setTimeout(function() { $('#alert_msg').hide(); }, 5000);
	$('#alert_msg').html('You had already found that word.');
	}
	else{
	setTimeout(function() { $('#alert_msg').hide(); }, 5000);
	$('#alert_msg').html('Sorry, thats a wrong combination.');
	}
});
$('#reveal_words').click(function(){
	bootbox.confirm({
	    message: "Are you sure you want to peep into the answer, your score will be locked if you proceed?",
	    buttons: {
	        confirm: {
	            label: "Yes, I'm sure",
	            className: 'btn-success'
	        },
	        cancel: {
	            label: 'No',
	            className: 'btn-danger'
	        }
	    },
	    callback: function (result) {
	    	$("#reveal_words_div").show();
	    	if(result){
				$('.reveal_div').remove();		    		
				$.each(dict_words, function( index, value ) {
						$('#reveal_words_div').append(value+',');
				});
				$('#reveal_words_div').text(function (_,txt) {
		    		return txt.slice(0, -1);
				});					    		
	    	}
	    }
	});
	
});
$("#submit_answer").click(function(){
	data = {"score": score, "found_list":found_values, "boggle_board":JSON.stringify(boogle_board), "words_list":dict_words};
	$.ajax({
			type: 'POST',
		url: "/answer-submit/",
		data: data,
		dataType: 'json',
		success: function (result) {
		bootbox.alert(result, function(){ window.location.href = "{{ url_for('pastgame') }}" });
		},
        error: function (e) {
          bootbox.alert(e, function(){ location.reload(); });
        }
	});
});