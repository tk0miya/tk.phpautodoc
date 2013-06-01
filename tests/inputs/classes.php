<?php

/**
 * here is docs for say_hello function
 */
function say_hello($name) {
  echo "hello " . $world; 
}

/**
 * here is docs for Hello class
 */
class Hello {
  /** here is docs for $attr1 */
  public $attr1 = 100;
  public $attr2 = null;

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

/**
 * here is docs for Goodbye class
 */
class Goodbye {
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
