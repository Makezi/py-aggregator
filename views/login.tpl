%rebase('base.tpl')
<div class="form-errors">
  %if errors: 
    %for error in errors:
    <p><strong>{{form}}:</strong> {{error}}</p>
    %end 
  %end
</div>
<div class="login-container">
  <div class="register">
    <form action="/register" method="POST">
      <legend>Register</legend>
      <p>
        <input type="text" name="username" placeholder="Username" required>
      </p>
      <p>
        <input type="password" name="password" placeholder="Password" required>
      </p>
      <p>
        <input type="password" name="verify_password" placeholder="Verify Password" required>
      </p>
      <p>
        <button type="submit" class="submit-button">Register</button>
      </p>
    </form>
  </div>
  <div class="login">
    <form action="/login" method="POST">
      <legend>Login</legend>
      <p>
        <input type="text" name="username" placeholder="Username" required>
      </p>
      <p>
        <input type="password" name="password" placeholder="Password" required>
      </p>
      <p>
        <button type="submit" class="submit-button">Login</button>
      </p>
    </form>
  </div>
</div>