%rebase('base.tpl')
<div class="form-errors">
  %if errors:
    %for error in errors:
      <p><strong>{{form}}:</strong> {{error}}</p>
    %end
  %end
</div>

<div class="submit-post">
  <form action="/submit_post" method="POST">
    <legend>Submit Post</legend>
      <p>Title</p>
      <p><textarea class="submit-title-box" name="title" required></textarea></p>
      <p>URL</p>
      <p><input type="text" name="url" placeholder="http://"></p>
      <p>Content</p>
      <p><textarea class="submit-content-box" name="content"></textarea></p>
      <p>Keywords</p>
      <div class="keyword-rules">
        <p>A keyword can be used to categorize your post with other similar posts</p>
        <ul>
          <li>Maximum  of 5 keywords</li>
          <li>15 characters per keyword</li>
          <li>Acceptable characters: [a-z 0-9 + # - .]</li>
          <li>Combine multiple words with dashes</li>
          <li>Delimit keywords with comma</li>
        </ul>
      </div>
      <p class="keywords-entered" style="margin-bottom: 20px;"></p>
      <input type="text" name="keywords" id="keywords">
      <p><button type="submit" class="submit-button">Submit</button></p>
  </form>
</div>

<script>
  $(document).ready(function(){
    // Focus out on comma or backspace
    $('#keywords').on('keyup', function(e){
      if(e.keyCode == 188 || e.keyCode == 8){
        $(this).focusout();
      }
    });

    $('#keywords').on('focusout', function(){
      var keywords = [];
      // Use comma as a delimiter
      var arr = this.value.split(',');
      var regex = /^[a-zA-Z0-9\+\-\.\#]+$/;
      for(var i = 0; i < arr.length; i++){
        arr[i] = arr[i].replace(/[^a-zA-Z0-9\+\-\.\#]/g,'');
        // No duplicates allowed in keywords array and maximum 5 only
        if(regex.test(arr[i]) && !($.inArray(arr[i], keywords) > -1)
            && keywords.length < 5 && arr[i].length <= 15){
          keywords.push(arr[i].toLowerCase());
        }
      }
      $('.keywords_entered').empty();
      // Create new keyword tag for each element in keyword array
      for(var i = 0; i < keywords.length; i++){
        $('.keywords_entered').append('<span class="keyword">'+ keywords[i].toLowerCase() +'</span>');
      }
    });
  });
</script>