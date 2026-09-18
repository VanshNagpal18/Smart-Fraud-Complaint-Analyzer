function Navbar() {
    return (
        <nav className="navbar">
             <div className="brand">
          <div className="brand-mark"><img src="Assets/logo.jpeg" alt="Logo" style={{ width: '100%', height: '100%' , borderRadius: '50%' }} /></div>
          <div>
            <div className="brand-name">C-DAC Project</div>
            &nbsp;
            <div className="brand-sub">Complaint Verification</div>
          </div>
        </div>
        <div className="nav-links">
          <a className="hide-mobile" href="#how">How it works</a>
          <a className="hide-mobile" href="#categories">Categories</a>
          <a className="nav-cta" href="#container">File a complaint</a>
        </div>
        </nav>
    );
}

export default Navbar;