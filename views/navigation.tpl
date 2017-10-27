<nav class="nav">
  <div class="wrap">
    <div class="nav-header">
      <h1>
        <a href="/">{{title}}</a>
      </h1>
    </div>
    <div class="nav-login">
      %if user:
      <ul>
        <li>Welcome {{user}}</li>
        <li>
          <a href="/logout">Logout</a>
        </li>
      </ul>
      %else:
      <ul>
        <li>
          <a href="/login">Login</a>
        </li>
        <li>
          <a href="/register">Register</a>
        </li>
      </ul>
      %end
    </div>
  </div>
</nav>