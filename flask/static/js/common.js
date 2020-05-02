function redirect(url) {
    window.location.href = url;
}

function replace(html) {
    $("html").html(html);
}

function get(url) {
    return $.ajax({
        url: url,
        type: "GET",
    });
}

function post(url, obj) {
    return $.ajax({
        url: url,
        type: "POST",
        data: JSON.stringify(obj),
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
