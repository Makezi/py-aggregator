<td class="vote-cell">
  <!-- Determine if user has already voted on this post -->
  %has_voted = False 
  %if post[10] is not None: 
  %has_voted = True 
  %end

  <!-- Restrict user from voting again by checking has_voted attribute -->
  <div class="vote" has_voted="{{has_voted}}">
    <!-- If vote was upvote, change color of upvote button -->
    %if post[10] == 1:
    <button type="button" class="vote-up-button" style="color:slategray">&#9650;</button>
    %else:
    <button type="button" class="vote-up-button">&#9650;</button>
    %end
    <span class="vote-value">{{post[9]}}</span>
    <!-- If vote was downvote, change color of downvote button -->
    %if post[10] == -1:
    <button type="button" class="vote-down-button" style="color:darkred">&#9660;</button>
    %else:
    <button type="button" class="vote-down-button">&#9660;</button>
    %end
  </div>
</td>
<td class="post-cell">
  <table>
    <tr>
      <td>
        <div class="post-image-thumbnail">
          %if post[3] is not None:
          <img src="./static/img/{{post[3]}}" />
          %end 
        </div>
      </td>
      <td>
        <div class="user-post">
          <img src={{post[7]}}>
          <strong>{{post[5]}}</strong>
          Posted {{post[6]}}
        </div>
        <div class="post-title-link">
          <!-- Indicate if post has external link -->
          %if post[2]:
          <div class="domain">
            <a href="{{post[2]}}">{{post[1]}}</a> (link)</div>
          %else:
          <div class="domain">
            <a href="/post/{{post[0]}}">{{post[1]}}</a>
          </div>
          %end
        </div>
        <div class="post-summary">
          <a href="/post/{{post[0]}}">{{post[8]}} comments</a>
        </div>
        <!-- Display post keywords if exists -->
        %if post[11]:
        <div class="post-keywords">
          %for keyword in post[11]:
          <span class="keyword">{{keyword}}</span>
          %end
        </div>
        %end
      </td>
    </tr>
  </table>
</td>