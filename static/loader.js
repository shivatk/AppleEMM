$('#sb').click(function(){
  $('#img').show(); //<----here
  $.ajax({
    ....
   success:function(result){
       $('#img').hide();  //<--- hide again
   }
}
