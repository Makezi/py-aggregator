%rebase('base.tpl')
<div class="post_container">
  <table>
    <tbody>
      <tr class="post" route="/post/{{post[0]}}">
        <td class="vote_cell">
            <!-- Determine if user has already voted on this post -->
            %has_voted = False
            %if post[9] is not None:
              %has_voted = True
            %end
            <div class="vote" has_voted="{{has_voted}}">
              <!-- Change vote button color depending on vote -->
              %if post[9] == 1:
              <button type="button" class="vote_up_button" style="color:slategray">&#9650;</button>
              %else:
              <button type="button" class="vote_up_button">&#9650;</button>
              %end
              <span class="vote_value">{{post[8]}}</span>
              %if post[9] == -1:
              <button type="button" class="vote_down_button" style="color:darkred">&#9660;</button>
              %else:
              <button type="button" class="vote_down_button">&#9660;</button>
              %end
            </div>
            <td class="post_cell">
              <div class="user_post">
                <img src={{post[7]}}> <strong>{{post[5]}}</strong>
                Posted {{post[6]}}
              </div>
              <div class="post_title_link">
                <h2>
                <!-- Indicate if post has external link -->
                %if post[2]:
                <div class="domain"><a href="{{post[2]}}">{{post[1]}}</a> (link)</div>
                %else:
                <div class="domain"><a href="/post/{{post[0]}}">{{post[1]}}</a></div>
                %end
                </h2>
              </div>

                % if post[3] is not None:
                <div class="post_image">
                %if post[3] is not None:
                <img src="/static/img/{{post[3]}}" />
                %end
                </div>
                % end
                <!-- Convert URLs to links -->
                % if post[4] is not None:
                  % import re
                  % r = re.compile(r"(https?://[^ ]+)")
                  % post[4] = r.sub(r'<a href="\1">\1</a>', post[4])
                  <p>{{!post[4]}}</p>
                % end
                <!-- Keywords -->
                %if post[10]:
                <div class="post_keywords">
                  %for keyword in post[10]:
                  <span class="keyword">{{keyword}}</span>
                  %end
                </div>
                %end
                <!-- Delete Post -->
                %if user == post[5]:
                <a href="/post/{{post[0]}}/delete">
                  <button class="delete_button"
                      onclick="return confirm('Are you sure you want to delete this post?')">
                    Delete Post
                  </button>
                </a>
                %end
            </td>
        </td>
      </tr>
    </tbody>
  </table>
  <h4>Comments</h4>
  <hr>
  <!-- Display comment box only if user logged in -->
  %if user:
  <div class="post_comment">
    <form action="{{request.path}}/submit_comment" method="POST">
      <li><textarea class="comment_box" name="comment"></textarea></li>
      <li><button type="submit" class="submit_button" id="comment_button">Submit</button></li>
    </form>
  </div>
  %end
  <!-- Display comments and nested comment hierarchy -->
  %def print_comment(comment, indent):
  <div class="comment" style="margin-left:{{indent}}">
    <table>
      <tbody>
        <tr route="/post/{{post[0]}}/comment/{{comment[0]}}">
          %include('comment_element.tpl', comment=comment)
        </tr>
    </table>
  </div>
  %end

  <div class="comments_container">
    %def create_node(parent, indent):
      %for comment in comments:
        %if comment[4] == parent[0]:
          %print_comment(comment, indent + 25)
          %parent.append([])
          %parent[len(parent)-1].append(create_node(comment, indent + 25))
        %end
      %end
      %return parent
    %end

    %for comment in comments:
      %if comment[4] is None:
        %print_comment(comment, 0)
        %create_node(comment, 0)
      %end
    %end
  </div>
</div>

<script>
  $(document).ready(function(){
    // Hide all nested comment boxes and submit buttons
    $('.comment_reply_form').hide();
    // Disable comment button by default
    $('#comment_button').attr('disabled', true);

    $('.comment_reply').click(function(){
      $('.comment_reply_form').hide();
      $(this).parent().children('.comment_reply_form').toggle();
      $(this).parent().children('.comment_reply_form').children().children('.comment_box').focus();
    });

    $('.cancel_button').click(function(){
      $('.comment_reply_form').hide();
    });

    // Enabled comment button only if comment box contains text
    $('.comment_box').keyup(function(){
      if($(this).val().length != 0){
        $('#comment_button').attr('disabled', false);
      }else{
        $('#comment_button').attr('disabled', true);
      }
    });

  });
</script>

%include('voting.tpl')