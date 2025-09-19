var gulp = require('gulp');
var path = require('path');
const sass = require('gulp-sass')(require('sass'));
var autoprefixer = require('gulp-autoprefixer');
var sourcemaps = require('gulp-sourcemaps');
var open = require('gulp-open');
var rename = require("gulp-rename");
var cleanCss = require('gulp-clean-css');
var minify = require('gulp-minify');

var Paths = {
    HERE: './',
    DIST: 'dist/',
    CSS: './css/',
    JS: './js',
    SCSS_TOOLKIT_SOURCES: './scss/soft-ui-dashboard.scss',
    SCSS: './scss/**/**'
};

gulp.task('scss', function() {
    return gulp.src(Paths.SCSS_TOOLKIT_SOURCES)
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(autoprefixer())
        .pipe(sourcemaps.write(Paths.HERE))
        .pipe(gulp.dest(Paths.CSS));
});


// Minify CSS
gulp.task('minify:css', function() {
    return gulp.src(Paths.CSS + '/soft-ui-dashboard.css')
        .pipe(cleanCss())
        .pipe(rename(function(path) {
            // Updates the object in-place
            path.extname = ".min.css";
        }))
        .pipe(gulp.dest(Paths.CSS))
});


// Js Minify
gulp.task('compress', function() {
  return gulp.src('./js'  + '/soft-ui-dashboard.js')
    .pipe(minify({
        ext:{
            src:'-min.js',
            min:'.min.js'
        }
    }))
    .pipe(gulp.dest(Paths.JS))
});

// Default
gulp.task('default', gulp.series('scss', 'minify:css','compress'));