$(document).ready(function () {
	var mealId = $("#favorite-icon").data("meal-id");
	$.ajax({
		url: "/meal/is_favorited/" + mealId,
		type: "GET",
		success: function (response) {
			if (response.isFavorited) {
				$("#favorite-icon").css("color", "red");
			} else {
				$("#favorite-icon").css("color", "grey");
			}
		},
	});
});

$("#favorite-icon").click(function () {
	var isFavorited = $(this).css("color") === "rgb(255, 0, 0)";
	var url = "/meal/toggle_favorite/" + mealId;
	$.ajax({
		url: url,
		type: "POST",
		success: function (response) {
			if (response.success) {
				$("#favorite-icon").css(
					"color",
					isFavorited ? "rgb(128, 128, 128)" : "rgb(255, 0, 0)"
				);
			}
		},
	});
});
