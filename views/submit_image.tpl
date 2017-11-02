%rebase('base.tpl')
<div class="form_errors">
  %if errors:
    %for error in errors:
      <p><strong>{{form}}:</strong> {{error}}</p>
    %end
  %end
</div>

<div class="submit_post">
  <form action="/submit_image" enctype="multipart/form-data" method="POST">
    <legend>Submit Image</legend>
    <p>Title</p>
    <p><textarea class="submit_title_box" name="title" required></textarea></p>
    <p>Image Upload</p>
    <p><input type="file" name="upload_image" placeholder=".jpg .png .gif"></p>
    <p>Keywords</p>
    <div class="keyword_rules">
      <p>A keyword can be used to categorize your post with other similar posts</p>
      <ul>
        <li>Maximum  of 5 keywords</li>
        <li>15 characters per keyword</li>
        <li>Acceptable characters: [a-z 0-9 + # - .]</li>
        <li>Combine multiple words with dashes</li>
        <li>Delimit keywords with comma</li>
      </ul>
    </div>
    <p class="keywords_entered" style="margin-bottom: 20px;"></p>
    <input type="text" name="keywords" id="keywords">
    <p><button type="submit" class="submit_button">Submit</button></p>
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