function get(url) {
    return $.ajax({
        url: url,
        type: "GET",
    });
}

function post(utl, obj) {
    return $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: JSON.stringify(j),
        contentType: 'application/json;charset=UTF-8',
    });
}

function jform(selector) {
    let j = $(selector).serializeArray().reduce(
        (obj, item) => {
            obj[item.name] = item.value;
            return obj;
        }, {});
    return j;
}

function redirect(url) {
    window.location.href = url;
}
