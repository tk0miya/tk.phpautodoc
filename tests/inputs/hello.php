<?php

/**
 * here is docs for say_hello function
 */
function say_hello($name) {
  echo "hello " . $world; 
}

function say_hello_undoc($name) {
  echo "hello " . $world; 
}

/**
 * here is docs for Hello class
 */
class Hello {
  /**
   * here is docs for world method
   */
  public function world($message = null) {
    $this->log($message);
  }

  public function world_undoc($message = null) {
    $this->log($message);
  }
}
?>
