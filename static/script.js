document.querySelectorAll(".external")
.forEach(a=>
    {
        a.addEventListener("click",e=>{const u=(a.href||"").trim();
            if(!/^https:\/\/(www\.)?(linkedin\.com|github\.com)\//i.test(u))
                {
                    e.preventDefault();
                    alert("Please enter a valid LinkedIn or GitHub profile.");
                    return
                }
                e.preventDefault();
                const w=window.open(u,"_blank","noopener,noreferrer");
                if(!w)window.location.href=u
            }
        )
    }
);