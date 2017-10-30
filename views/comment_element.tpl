<td class="vote-cell">
  <!--Determine if user has already voted on this comment -->
  %has_voted = False
  %if comment[8] is not None:
      %has_voted = True
  %end
  <!-- Restrict user from voting again by checking has_voted attribute -->
  <div class="vote" has_voted="{{has_voted}}">
    <!-- If vote was upvote, change color of upvote button -->
    %if comment[8] == 1:
      <button type="button" class="vote-up-button" style="color:slategray">&#9650;</button>
    %else:
      <button type="button" class="vote-up-button">&#9650;</button>
    %end
    <span class="vote-value">{{comment[7]}}</span>
    <!-- If vote was downvote, change color of downvote button -->
    %if comment[8] == -1:
      <button type="button" class="vote-down-button" style="color:darkred">&#9660;</button>
    %else:
      <button type="button" class="vote-down-button">&#9660;</button>
    %end
  </div>
</td>
<td class="comment-cell">
  <div class="user-post">
    <img src={{comment[6]}}> <strong>{{comment[2]}}</strong>
    Posted {{comment[5]}}
  </div>
  <div class="comment-body">
    <!-- Convert URLs to links -->
    % import re
    % r = re.compile(r"(https?://[^ ]+)")
    % comment[1] = r.sub(r'<a href="\1">\1</a>', comment[1])
    {{!comment[1]}}
  </div>
  <!-- If a user is logged in, display reply button and fields -->
  %if user:
    <a href="javascript:void(0)" class="comment_-eply">reply</a>
    <form class="comment-reply-form" action="{{request.path}}/submit_comment" method="POST">
      <li><textarea class="comment-box" name="comment"></textarea></li>
      <li>
        <button type="submit" class="submit-button">Submit</button>
        <button type="button" class="cancel-button">Cancel</button>
      </li>
      <input type="hidden" name="parent" value="{{comment[0]}}">
    </form>
  %end
</td>