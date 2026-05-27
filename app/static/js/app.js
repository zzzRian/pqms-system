// PQMS – ligero
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.alert').forEach(a=>setTimeout(()=>{
    if(window.bootstrap){bootstrap.Alert.getOrCreateInstance(a).close()}
  },6000));
});
