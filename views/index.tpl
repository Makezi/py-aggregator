%rebase('base.tpl')

<div class="index_container">
  <div class="search_box">
    <form action="/search" method="GET">
      <p>
        <input type="search" name="post_search" placeholder="Search...">
      </p>
      <p>
        <button type="submit" class="submit_button">
          <img src="http://www.clker.com/cliparts/n/U/H/1/H/u/search-icon-white-one-md.png" alt="Search Icon">
        </button>
      </p>
    </form>
  </div>

  <div class="submit_post_container">
    %if user:
    <a href="/submit_post">
      <button class="submit_button">Submit Post</button>
    </a>
    <a href="/submit_image">
      <button class="submit_button">Submit Image</button>
    </a>
    %end
  </div>

  <div class="posts_container">
    %if posts:
    <table>
      %for post in posts:
      <tbody>
        <tr class="post" route="/post/{{post[0]}}">
          %include('post_element.tpl', post=post)
        </tr>
      </tbody>
      %end
    </table>
    %end
  </div>
</div>

%include('voting.tpl')