
const formConstructor = (item) => {
    // create form
    const form = document.getElementById('form')
    form.className = 'd-flex flex-wrap gap-2 p-2 justify-content-center'
    form.innerHTML = ''

    console.log(item)

    const avatarContainer = document.createElement('div')
    avatarContainer.className = 'd-flex w-90 flex-column gap-1'

    const avatarImg = document.createElement('img')
    avatarImg.setAttribute('src',item.image ? item.image : `${staticAddress}/img/team-4.jpg`);
    avatarImg.className = 'avatar avatar-xl me-3'
    avatarImg.id = 'avatar-img'

    const avatarInput = document.createElement('input')
    avatarInput.setAttribute('type','file')
    avatarInput.className = ''
    avatarInput.setAttribute('accept','accept="image/*')
    avatarInput.name = 'avatar-input'
    avatarInput.id = 'avatar-input'

    avatarContainer.appendChild(avatarImg)
    avatarContainer.appendChild(avatarInput)

    form.innerHTML += avatarContainer.outerHTML

    for (let i in item) {

        if (i !== 'image' && i !== 'registration_date' && i !== 'status') {

            const inputContainer = document.createElement('div')
            inputContainer.className = 'w-45'
            inputContainer.className += (i === 'address' ? ' w-90' : '')

            const label = document.createElement('label')
            label.setAttribute('htmlFor', i)
            label.innerHTML = i[0].toUpperCase() + i.slice(1,i.length);;
            label.className = "form-label m-0";

            const input = document.createElement('input');
            input.setAttribute('type', 'text');
            input.className = 'form-control m-0'
            input.name = i

            if (i === 'email')
                input.setAttribute('readonly', 'true')

            if (i === 'username')
                inputContainer.setAttribute('hidden', 'true')

            input.setAttribute('value', item[i])

            inputContainer.appendChild(label)
            inputContainer.appendChild(input)

            form.innerHTML += inputContainer.outerHTML
        }
    }

    document.getElementById('avatar-input').onchange = (e) => {
        document.getElementById('avatar-img').setAttribute('src', URL.createObjectURL(e.target.files[0]))
    }

    return form;
}