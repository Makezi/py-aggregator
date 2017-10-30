<script>
  $(document).ready(function(){
    // Vote up button
    $('.vote_up_button').click(function(){
      // Perform on click only if user is logged in
      %if user:
        // Make reference to self (so we can change css after POST)
        var self = $(this);
        var route = $(this).parent().parent().parent().attr('route') + '/vote_up'
        var vote_value = $(this).parent().children('.vote_value');
        var has_voted = $(this).parent().attr('has_voted');
        // Send POST only if the user hasn't already voted
        if(has_voted != "True"){
          $.post(route, function(response){
            self.parent().attr('has_voted', 'True')
            self.css('color', 'slategray');
            // Retrieve response with new vote value
            vote_value.html(response);
          });
        }
      %else:
        // Redirect to /login if user does not exist
        window.location = '/login';
      %end
    });

    // Vote down button
    $('.vote_down_button').click(function(){
      // Perform on click only if user is logged in
      %if user:
        // Make reference to self (so we can change css after POST)
        var self = $(this);
        var route = $(this).parent().parent().parent().attr('route') + '/vote_down'
        var vote_value = $(this).parent().children('.vote_value');
        var has_voted = $(this).parent().attr('has_voted');
        // Send POST only if the user hasn't already voted
        if(has_voted != "True"){
          $.post(route, function(response){
            self.parent().attr('has_voted', 'True')
            self.css('color', 'darkred');
            // Retrieve response with new vote value
            vote_value.html(response);
          });
        }
      %else:
        // Redirect to /login if user does not exist
        window.location = '/login';
      %end
    });
  });
</script>