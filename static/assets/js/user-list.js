const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value
let deleteId = ''
document.querySelector('#user-list-table').addEventListener('click', (e) => {
    if (e.target.nodeName === 'BUTTON' || e.target.nodeName === 'I') {
        if (e.target.className.includes('edit')) {
            formConstructor( myData.data.filter(d => d.username === e.target.id)[0] )
        } else if (e.target.className.includes('delete')) {
            deleteId = (e.target.id)
        }
    } else if (e.target.nodeName === 'INPUT') {
        if (e.target.className.includes('status'))
            changeStatusAction(e.target.id , e.target.checked ? 1 : 0)
    }
})

const changeStatusAction = (id,data) => {
    fetch(`/user/${id}/`,{
        method: 'PUT',
        body: {status: data},
        headers: {'X-CSRFToken' : csrfToken}
    })
        .then((response) => response.json())
        .then((result) => {location.reload()})
        .catch((err) => {console.log(err)})
}