
var svg=d3.select("#heatmap");
    
var w = 600;
var h = 600;
var padding = 70;  
      
var TimeOfDay =[];
var DayOfWeek = [];
var DayTimeMatrix=[];
var DayTimeMatrixFill = [];
var max_score ;
var min_score ;
var max_sample_size;
var ScoreOfInterest ="Avg_Cultural_Score";
var FullScoreArray=[];
var InterviewerArray=[];

// var days_of_week = {'Mon' : 0,'Tue' : 1,'Wed' : 2,'Thu' : 3,'Fri' : 4,'Sat' : 5,'Sun' : 6};
 var DayOfWeek = ['Mon','Tue','Wed','Thu','Fri'];
 var TimeOfDay=[10,11,12,13,14,15,16,17,18];

TimeOfDay.sort(function(a, b){return a - b;});

// helper functions
function clone(obj){   
  return JSON.parse(JSON.stringify(obj));
}   
     
function parseIntOrLeaveString(stringValue){
  var result = parseInt(stringValue);
  if (isNaN(result)){
      result = stringValue;
  }
  return result;
}

function get_keys(dict){
  var keys = [];
  for(var k in dict) keys.push(parseIntOrLeaveString(k));
  return keys;
}

function lookupDayTime( dtarray,day,hour) {
  for(var i = 0; i < dtarray.length; i++)
    if( dtarray[i].Day === day && dtarray[i].Hour === hour)
        return i;
    return -1;
}


   
window.onload = function(){
    make_ajax_request("api/scores_by_time_stats",loadHeatMap,  null);

}



function loadHeatMap(ajaxResult) {

  //filter to work week data only
  for (var i = 0; i < ajaxResult.length; i++)    
    if (DayOfWeek.indexOf(ajaxResult[i].Day) > -1 && TimeOfDay.indexOf(ajaxResult[i].Hour) > -1 )
        FullScoreArray.push(ajaxResult[i]);     

  drawChartBones();
  updateHeatMapandInterviewerList(FullScoreArray,ScoreOfInterest);    
  setUpInterviewerSearch(); 
}


function updateHeatMapandInterviewerList(ScoreArray,ScoreOfInterest){

  updateDayTimeMatrix(ScoreArray);
  updateInterviewerArray(ScoreArray);
  updateChartData(ScoreOfInterest);
  updateChart(ScoreOfInterest); 
  updateInterviewerList(InterviewerArray); 

}



function updateHeatMap(FilterTerm,ScoreOfInterest){

  var FilteredScoreArray=getFilteredScoresArray(FullScoreArray,FilterTerm,ScoreOfInterest); 
 // InterviewerArray=updateInterviewerArray(FilteredScoreArray);
  updateDayTimeMatrix(FilteredScoreArray);
  updateChartData(ScoreOfInterest);
  updateChart(ScoreOfInterest); 
 // updateInterviewerList(InterviewerArray); 

 }


function updateDayTimeMatrix(ScoreArray){
  
  DayTimeMatrixFill=[];
  DayTimeMatrix=[];

  for (var i=0;i<DayOfWeek.length;i++)
   for (var j=0;j<TimeOfDay.length;j++)  
      DayTimeMatrixFill.push({Day : DayOfWeek[i],Hour : TimeOfDay[j]});

  for (var i = 0; i < ScoreArray.length; i++) 
  {
      
      var j=lookupDayTime(DayTimeMatrix,ScoreArray[i].Day,ScoreArray[i].Hour);
      
      //remove this element from DayTimeMatrixFill
      var k=lookupDayTime(DayTimeMatrixFill,ScoreArray[i].Day,ScoreArray[i].Hour);
      if (k>-1)
        DayTimeMatrixFill.splice(k,1);

      if (j==-1) 
      {

        DayTimeMatrix.push(
            {Avg_Technical_Score : ScoreArray[i].Avg_Technical_Score
            ,Hour : ScoreArray[i].Hour
            ,Sample_Size : ScoreArray[i].Sample_Size
            ,Avg_Cultural_Score : ScoreArray[i].Avg_Cultural_Score
            ,Day : ScoreArray[i].Day}
            );
        }
    else
      {
        DayTimeMatrix[j].Avg_Technical_Score=(DayTimeMatrix[j].Avg_Technical_Score+ScoreArray[i].Avg_Technical_Score)/2
        DayTimeMatrix[j].Avg_Cultural_Score=(DayTimeMatrix[j].Avg_Cultural_Score+ScoreArray[i].Avg_Cultural_Score)/2
        DayTimeMatrix[j].Sample_Size=(DayTimeMatrix[j].Sample_Size+ScoreArray[i].Sample_Size)
      } 
    }             
}

function updateInterviewerArray(FullScoreArray){
  InterviewerArray=[];
  var InterviewerAssocArray ={};  
  for (var i = 0; i < FullScoreArray.length; i++)
  {
    InterviewerAssocArray[FullScoreArray[i].Interviewer.email] = FullScoreArray[i].Interviewer
  }

  //copy assoc array into regular
  for (var k in InterviewerAssocArray)
        if (InterviewerAssocArray.hasOwnProperty(k))
            InterviewerArray.push(InterviewerAssocArray[k]);    
}  


function getFilteredScoresArray(FullScoreArray,FilterTerm,ScoreOfInterest,team){       
  var FilteredScoreArray = [];

  if (FilterTerm == "")
  {
    for (var i = 0; i < FullScoreArray.length; i++)
      if (FullScoreArray[i][ScoreOfInterest] != null)
        FilteredScoreArray.push(FullScoreArray[i]);
  }  
    
  else    
   {
    for (var i = 0; i < FullScoreArray.length; i++)
          if (FullScoreArray[i].Interviewer.name.match(new RegExp(FilterTerm, "gi")) && FullScoreArray[i][ScoreOfInterest] != null)
              FilteredScoreArray.push(FullScoreArray[i]);
   }
  
  return FilteredScoreArray ;
}


var filter_interviewers = function(){
  var FilterTerm = d3.select(".interviewer-textfield").node().value;
  var FilteredScoreArray = [];
  FilteredScoreArray=getFilteredScoresArray(FullScoreArray,FilterTerm,ScoreOfInterest); 
  updateHeatMapandInterviewerList(FilteredScoreArray,ScoreOfInterest); 
}





function setUpInterviewerSearch(){

  var CultScore = d3.select("#cult_score_all");
  var TechScore = d3.select("#tech_score_all");

   CultScore. 
    on("mouseover", function(data)
   {ScoreOfInterest='Avg_Cultural_Score' 
    TechScore.classed("highlighted", false);
    d3.select(this).classed("highlighted", true);
    filter_interviewers();
   });

  TechScore. 
  on("mouseover", function(data)
   {ScoreOfInterest='Avg_Technical_Score'           
    CultScore.classed("highlighted", false);
    d3.select(this).classed("highlighted", true);        
    filter_interviewers();
  });

  
  d3.select(".interviewer-textfield").on("input", function(){
    filter_interviewers();}
    ); 
}

 
function updateChartData(ScoreOfInterest){
  max_score = 4;
  min_score = 1;
  max_sample_size=0;
  var times_of_day_dict = {};
  var days_of_week_dict = {};

   // not sure if I need this code
  for (var i = 0; i < DayTimeMatrix.length; i++)
  {
      times_of_day_dict[DayTimeMatrix[i].Hour] = true;
      days_of_week_dict[DayTimeMatrix[i].Day] = true;
      if (DayTimeMatrix[i][ScoreOfInterest] === null)
            continue;
      if (DayTimeMatrix[i]["Sample_Size"] > max_sample_size)
      {
        max_sample_size=DayTimeMatrix[i]["Sample_Size"];
      }
  }
}  

 

function drawChartBones(){
  var yTickScale = d3.scale.ordinal().domain(d3.range(TimeOfDay.length)).rangeRoundBands([padding, w - padding * 2]);
  var xTickScale =d3.scale.ordinal() .domain(d3.range(DayOfWeek.length)).rangeRoundBands([padding, h - padding]);
   
      //  Draw Axis
      
  var xAxis = d3.svg.axis().scale(xTickScale).orient("top").tickValues(DayOfWeek);
  var yAxis = d3.svg.axis().scale(yTickScale).orient("left").tickValues(TimeOfDay);
  svg.append("g").attr("class", "axis").attr("transform", "translate(0," + padding + ")").call(xAxis);     
  svg.append("g").attr("class", "axis").attr("transform", "translate(" + padding + ",0)").call(yAxis);                  

}          
    
function updateChart(ScoreOfInterest){

  var yScale = d3.scale.ordinal().domain(d3.range(TimeOfDay.length)).rangeRoundBands([padding, w - padding * 2],0);
  var xScale = d3.scale.ordinal().domain(d3.range(DayOfWeek.length)).rangeRoundBands([padding, h - padding],0.15); 

      
  var bars = svg.selectAll("svg").data(DayTimeMatrix, function(d){return TimeOfDay.indexOf(d.Hour)*10+DayOfWeek.indexOf(d.Day);})
  bars
  .enter()
  .append("svg")
    .attr("y", function(d) {return yScale(TimeOfDay.indexOf(d.Hour));})
    .attr("x", function(d) {return xScale(DayOfWeek.indexOf(d.Day));})         
    .attr("width", xScale.rangeBand())
    .attr("height", yScale.rangeBand());

  bars.append("rect")
  .attr("y", 0)
  .attr("x", 0) 
  .attr("width", xScale.rangeBand())
  .attr("height", yScale.rangeBand())
  .attr("opacity",1)
  .style("fill", function(d) 
  {
    if (d[ScoreOfInterest] === null)
    {
      return "rgba(0, 0, 0, 0)";
    }
    var color_offset_r = Math.round(((d[ScoreOfInterest] - min_score)/(max_score - min_score)) * 110);
    var color_offset_g = Math.round(((d[ScoreOfInterest] - min_score)/(max_score - min_score)) * 216);
    var color_offset_b = Math.round(((d[ScoreOfInterest] - min_score)/(max_score - min_score)) * 255);


    var ret_value = "rgb(" + (248 - color_offset_r).toString()
                + ","+(0+ color_offset_g).toString() 
                + ","+ (0 + color_offset_b).toString()
                + ")";
    return ret_value;
  });
  

  bars.exit().remove(); 


  var barsfill = svg.selectAll("svg").data(DayTimeMatrixFill, function(d){return TimeOfDay.indexOf(d.Hour)*10+DayOfWeek.indexOf(d.Day);})
  
  barsfill
  .enter()
  .append("svg")

    .attr("y", function(d, i) {return yScale(TimeOfDay.indexOf(d.Hour));})
    .attr("x", function(d, i) {return xScale(DayOfWeek.indexOf(d.Day));}) 
    .attr("width", xScale.rangeBand())
    .attr("height", yScale.rangeBand()); 
    

  barsfill
    .append('defs')
    .append('pattern')
      .attr('id', 'diagonalHatch')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 4)
      .attr('height', 4)
    .append('path')
      .attr('d', 'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2')
      .attr('stroke', 'lightgray')
      .attr('stroke-width', 1);

    barsfill.append("rect")
        .attr("x", 0)
        .attr("width", 100)
        .attr("height", 100)
        .style("fill", 'none');

    barsfill.append("rect")
      .attr("x", 0)
      .attr("width", 100)
      .attr("height", 100)
      .attr('fill', 'url(#diagonalHatch)');

        
    barsfill.attr("id","fillpattern");

     bars
      .append("text")
     .attr("y", function(d, i) {return yScale.rangeBand()/2+5;})
      .attr("x", function(d, i) {return xScale.rangeBand()/2;})  
      .attr("text-anchor","middle")
      .attr("fill","white")
      .attr("font-family","sans-serif")
      .attr("font-size","11px")
      .text(function(d,i) {  if (d[ScoreOfInterest] !=null) return d[ScoreOfInterest].toFixed(1);})

      bars
      .append("text")
      .attr("y", function(d, i) {return yScale.rangeBand()/2+10;})
      .attr("x", function(d, i) {return xScale.rangeBand()/2+20;})  
      .attr("fill","white")
      .attr("font-family","sans-serif")
      .attr("font-size","8px")
      .text(function(d,i) {  if (d[ScoreOfInterest] !=null) return "{"+ (d["Sample_Size"].toString()).toString()+"}";})

  }       

function updateInterviewerList(interviewer_array){
  var tableview = d3.select("#interviewer-list-tableview");
  var tableview_cells = tableview.selectAll(".tableview-cell").data(interviewer_array);
  var inner_tableviewcell_div = tableview_cells.enter().
      append("div").
          classed("tableview-cell", true).
          classed("non_selectable", true).
          style("cursor", "default");
    tableview_cells.append("div");

       tableview_cells.exit().remove();   

  inner_tableviewcell_div.append("div").
      classed("interviewer_avatar_frame", true).
      style("position", "relative").
      append("div").
          style("color", "rgb(255, 255, 255)").
          style("text-align", "center").
          style("line-height", "35px");
   tableview.selectAll(".interviewer_avatar_frame").data(interviewer_array).select("div").
           style("background-image", function(data)
           {
               var background_image = "";
               if (data.avatar_url)
               {
                   background_image = "url('" + data.avatar_url + "')";
               }
               return background_image;
           }).
           style("background-color", function(data)
           {
               var background_color = "";
               if (!data.avatar_url)
               {
                   background_color = "rgb(72, 195, 252)";
               }
               return background_color;
           }).
           text(function(data)
           {
               var initials = "";
               if (!data.avatar_url)
               {
                  initials = (data.name.charAt(0) + data.name.split(/\s/).pop().charAt(0)).toUpperCase();
               }
               return initials;
           });
  inner_tableviewcell_div.append("div").
      classed("interviewer_name", true).
      style("position", "relative");
  tableview.selectAll(".interviewer_name").data(interviewer_array).
      text(function(data, i){return data.name;});

  inner_tableviewcell_div.append("div").classed("Cult_score_selector", true).style("float", "right").style("width", "30%");
     tableview.selectAll(".Cult_score_selector").text("Cultural");
  inner_tableviewcell_div.append("div").classed("tech_score_selector", true).style("float", "right").style("width", "30%");
    tableview.selectAll(".tech_score_selector").text("Technical");
   tableview.selectAll(".Cult_score_selector").data(interviewer_array). 
      on("mouseover", function(data)
       {
          // d3.event.stopPropagation();
          // console.log(data.name)
           d3.select(this).classed("highlighted", true);

           updateHeatMap(data.name,"Avg_Cultural_Score");
  
       })
      .on("mouseout", function(data)        {
          d3.select(this).classed("highlighted", false);
          var FilterTerm = d3.select(".interviewer-textfield").node().value;
          updateHeatMap(FilterTerm,ScoreOfInterest);
       })    
      ;

  tableview.selectAll(".tech_score_selector").data(interviewer_array). 
      on("mouseover", function(data) 
        {  //d3.event.stopPropagation(); 
          // console.log(data.name)         
           d3.select(this).classed("highlighted", true);
          updateHeatMap(data.name,"Avg_Technical_Score");
       })      
      .on("mouseout", function(data)        {
           d3.select(this).classed("highlighted", false);
          var FilterTerm = d3.select(".interviewer-textfield").node().value;
          updateHeatMap(FilterTerm,ScoreOfInterest);
       }) ;

}
